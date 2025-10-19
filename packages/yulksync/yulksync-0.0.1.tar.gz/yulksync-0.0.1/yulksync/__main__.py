# 2025.10.18   python -m yulksync en/cn/all
import requests,os,fire # fire>=0.7.1  wget>=3.2
host	= 'file.yulk.net'
root	= os.path.dirname(os.path.abspath(__file__)).replace('yulksync','yulk') 

def download_with_wget(url, local_filename):
	import wget
	try:
		if os.path.exists(local_filename):
			os.remove(local_filename)
		print ("Start to download: ",  url , flush=True) 
		wget.download(url, local_filename)
		print(f"\nDone: {local_filename}")
	except Exception as e:
		print(f"\nFailed: {e}", url, local_filename)

def run(name): 
	''' python -m yulksync en/cn/all/par/park/parkv/parx/myu/ce | python -m yulksync par/myusnt.parquet '''
	if name.endswith('.parquet'):  # python -m yulksync par/ce.parquet
		download_with_wget(f"http://{host}/{name}", f"{root}/{name}")
	else:
		for line in requests.get(f"http://{host}/yulksync/{name}.txt").text.strip().split('\n'):  # par/myu.parquet
			try:
				line = line.strip()
				if not line: continue 
				print (line, flush=True)
				download_with_wget(f"http://{host}/{line}", f"{root}/{line}")
			except Exception as e:
				print(f"\nFailed: {e}", line, root)

if __name__ == "__main__": 	
	fire.Fire(run)
