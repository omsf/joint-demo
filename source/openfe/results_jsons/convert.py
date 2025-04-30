import gufe
import json
import sys

with open(f"../results_jsons/{sys.argv[1]}", 'r') as stream:
    dicter = json.loads(stream.read(), cls=gufe.tokenization.JSON_HANDLER.decoder)

for unit in dicter['unit_results']:
    dicter['unit_results'][unit]['outputs']['structural_analysis'] = None

for unit in dicter['protocol_result']['data']:
    dicter['protocol_result']['data'][unit][0]['outputs']['structural_analysis'] = None
    
with open(sys.argv[1], 'w') as stream:
    json.dump(dicter, stream, cls=gufe.tokenization.JSON_HANDLER.encoder)
