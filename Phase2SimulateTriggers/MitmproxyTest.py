import os
import base64
import io
from mitmproxy.io import FlowReader
from mitmproxy.addons import export
#################################### METHOD 1 #################################################
# # e.g.: https://developers.refinitiv.com/article/use-mitmdump-capture-edp-rt-content
# Command: sudo -u mitmproxyuser bash -c '$HOME/.local/bin/mitmdump --mode transparent --showhost -w content.log --flow-detail 3 --set stream_websocket=true'
# unknown_dir = os.system("sudo -u mitmproxyuser bash -c '$HOME/.local/bin/mitmdump -r $HOME/.local/bin/content.log --flow-detail 3'" )
# print(unknown_dir)


#################################### METHOD 2 #################################################
# e.g.: https://avilpage.com/2018/08/parsing-and-transforming-mitmproxy-request-flows.html
# Command: sudo -u mitmproxyuser bash -c '$HOME/.local/bin/mitmdump --mode transparent --showhost -w content.mitm --flow-detail 3 --set stream_websocket=true'
filename = '/home/mitmproxyuser/.local/bin/content.mitm'

with open(filename, 'rb') as fp:
    reader = FlowReader(fp)

    for flow in reader.stream():
        print('##########################################################')
        print(flow.request.url)
        print(flow.request)
        print(flow.response)
        print(export.raw(flow))
        print(export.httpie_command(flow))