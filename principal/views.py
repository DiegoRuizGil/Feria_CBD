from django.shortcuts import render
from .forms import BuscadorCasetas
import pymongo
from django.core.paginator import Paginator


def home(request):

    return render(request, "home.html", {})

def buscador_titulo(request):
    results = []

    if request.method == 'GET':
        titulo = request.GET.get('titulo')

        client = pymongo.MongoClient()

        db = client.feria
        collection = db.casetas

        pipeline = [
            {
                "$match": {
                    "TITULO": {
                        "$regex": f'.*{titulo}.*',
                        "$options": "i"
                    }
                }
            }
        ]

        results = list(collection.aggregate(pipeline))

        print(f'Resultados: {len(results)}')

    paginator = Paginator(results, 12)
    page = request.GET.get('page') or 1
    results = paginator.get_page(page)
    current_page = int(page)
    pages = range(1, results.paginator.num_pages + 1)

    context = {
        "results": results,
        "pages": pages,
        "current_page": current_page,
    }

    return render(request, 'buscador_titulo.html', context)

def buscador_acceso(request):
    results = []

    if request.method == 'GET':
        tipo_acceso = request.GET.get('tipo_acceso')

        client = pymongo.MongoClient()

        db = client.feria
        collection = db.casetas

        pipeline = [
            {
                "$lookup": {
                    "from": "accesos",
                    "localField": "ID",
                    "foreignField": "ID",
                    "as": "accesos_casetas"
                }
            },
            {
                "$project": {
                    "_id": "$ID",
                    "titulo": "$TITULO",
                    "calle": "$CALLE",
                    "numero": "$NUMERO",
                    "modulos": "$MODULOS",
                    "clase": "$CLASE",
                    "entidad": "$ENTIDAD",
                    "id_calle": "$ID_CALLE",
                    "acceso": { "$arrayElemAt": ["$accesos_casetas.ACCESO", 0] }
                }
            },
            {
                "$match": {
                    "acceso": f'{tipo_acceso}'
                }
            }
        ]

        results = list(collection.aggregate(pipeline))
        
        print(f'Resultados: {len(results)}')

    context = {
        "results": results,
    }

    return render(request, 'buscador_acceso.html', context)


def buscador_calles(request):
    results = []

    if request.method == 'GET':
        calle_seleccionada = request.GET.get('calle')

        client = pymongo.MongoClient()

        db = client.feria
        collection = db.casetas

        pipeline_group = [
            {
                "$group": {
                    "_id": "$CALLE",
                    "total": {
                        "$sum": 1
                    }
                }
            }
        ]

        results_group = list(collection.aggregate(pipeline_group))

        calle_num_casetas = {}
        for result in results_group:
            calle_num_casetas[result['_id']] = result['total']


    capacidad_calle = 0
    if calle_seleccionada is not None:
        capacidad_calle = calle_num_casetas[calle_seleccionada]

        pipeline_match = [
            {
                "$match": {
                    "CALLE": f'{calle_seleccionada}'
                }
            }
        ]

        results = list(collection.aggregate(pipeline_match))

    context = {
        "results": results,
        "calles": list(calle_num_casetas.keys()),
        "calle_seleccionada": calle_seleccionada,
        "capacidad_calle": capacidad_calle,
    }

    return render(request, 'buscador_calles.html', context)




def posiciones(request):

    results = []

    if request.method == 'GET':
        coords = request.GET.get('coords')
        print(coords)

        if coords is not None:

            latitude = float(coords.split(',')[0])
            longitude = float(coords.split(',')[1])

            client = pymongo.MongoClient()

            db = client.feria
            collection = db.localizaciones

            pipeline = [
                {
                    "$geoNear": {
                        "near": {
                            "type": "Point",
                            "coordinates": [
                                latitude, longitude,
                            ],
                        },
                        "distanceField": "distance",
                        "spherical": True,
                    }
                },
                {
                    "$limit": 12
                },
                {
                    "$lookup": {
                        "from": "casetas",
                        "localField": "ID",
                        "foreignField": "ID",
                        "as": "caseta",
                    }
                },
                {
                    "$lookup": {
                        "from": "accesos",
                        "localField": "ID",
                        "foreignField": "ID",
                        "as": "acceso",
                    }
                },
                {
                    "$lookup": {
                        "from": "capacidades",
                        "localField": "ID",
                        "foreignField": "ID",
                        "as": "capacidad",
                    }
                },
                {
                    "$project": {
                        "_id": "$ID",
                        "latitude": "$LATITUDE",
                        "longitude": "$LONGITUDE",
                        "distance": "$distance",
                        "titulo": { "$arrayElemAt": ["$caseta.TITULO", 0] },
                        "calle": { "$arrayElemAt": ["$caseta.CALLE", 0] },
                        "numero": { "$arrayElemAt": ["$caseta.NUMERO", 0] },
                        "modulos": { "$arrayElemAt": ["$caseta.MODULOS", 0] },
                        "clase": { "$arrayElemAt": ["$caseta.CLASE", 0] },
                        "entidad": { "$arrayElemAt": ["$caseta.ENTIDAD", 0] },
                        "id_calle": { "$arrayElemAt": ["$caseta.ID_CALLE", 0] },
                        "acceso": { "$arrayElemAt": ["$acceso.ACCESO", 0] },
                        "capacidad": { "$arrayElemAt": ["$capacidad.CAPACIDAD", 0] },
                    }
                }
            ]

            results = list(collection.aggregate(pipeline))

    context = {
        "results": results,
    }

    return render(request, 'posiciones.html', context)