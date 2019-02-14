from django.http import JsonResponse
from askcos_site.askcos_celery.contextrecommender.cr_nn_worker import get_n_conditions as neighbor_get_n_conditions
from askcos_site.askcos_celery.contextrecommender.cr_network_worker import get_n_conditions as network_get_n_conditions

def neural_network(request):
    resp = {}
    reactants = request.GET.get('reactants')
    products = request.GET.get('products')
    rxn = reactants+'>>'+products
    n = request.GET.get('n', 10)
    singleSlvt = request.GET.get('singleSlvt', True)
    with_smiles = request.GET.get('with_smiles', True)
    return_scores = request.GET.get('return_scores', False)
    res = network_get_n_conditions.delay(rxn, n, singleSlvt, with_smiles, return_scores)
    contexts = res.get(60)
    json_contexts = []
    for context in contexts:
        c = {
            'temperature': context[0],
            'solvent': context[1],
            'reagent': context[2],
            'catalyst': context[3],
            'time': context[4],
            'yield': context[5],
        }
        json_contexts.append(c)
    resp['contexts'] = json_contexts
    return JsonResponse(resp)