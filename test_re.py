
import re
from mininet.util import quietRun



masuk = [('1', '1'), ('1', '2'), ('2', '4')]


def getQueueConfigs(portsList):
	result=[]
	prev = -1
	for port,queue_id in portsList:
		current = port
		if (current != prev):
			cmd = 'sudo dpctl unix:/tmp/s1 queue-get-config %d' %int(port)
			cmdresult = quietRun(cmd)
			cmdresult = re.findall('q="(\d+)", props=\[minrate\{rate="(\d+)"\}\]', cmdresult)
			#build the json friendly here
			anArray=[]
			for queueID,minrate in cmdresult:
				adict = {"queue_id":queue_id,"min_rate":minrate}
				anArray.append(adict)
			result.append({"port_name": port, "queues":anArray})
		prev = current
	return result




print getQueueConfigs(masuk)




