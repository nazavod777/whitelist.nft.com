from web3.auto import w3
from sys import stderr, exit
from requests import Session
from pyuseragents import random as random_useragent
from capmonster_python import RecaptchaV2Task, CapmonsterException
from msvcrt import getch
from os import system
from urllib3 import disable_warnings
from loguru import logger
from platform import system as platform_system
from platform import platform
from multiprocessing.dummy import Pool
from dotenv import dotenv_values
from random import randint

disable_warnings()
def clear(): return system('cls' if platform_system() == "Windows" else 'clear')
logger.remove()
logger.add(stderr, format="<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <cyan>{line}</cyan> - <white>{message}</white>")

if 'Windows' in platform():
	from ctypes import windll
	windll.kernel32.SetConsoleTitleW('NFT.com Auto Reger | by NAZAVOD')

def create_wallet():
	account = w3.eth.account.create()
	privatekey = str(account.privateKey.hex())
	address = str(account.address)
	return(address, privatekey)

class Wrong_Response(BaseException):
	def __init__(self, message):
		self.message = message

def random_tor_proxy():
	proxy_auth = str(randint(1, 0x7fffffff)) + ':' + str(randint(1, 0x7fffffff))
	proxies = {'http': 'socks5://{}@localhost:9150'.format(proxy_auth), 'https': 'socks5://{}@localhost:9150'.format(proxy_auth)}
	return(proxies)

def take_proxies(length):
	proxies = []

	while len(proxies) < length:
		with open(proxy_folder, 'r') as file:
			for row in file:
				proxies.append(row.strip())

	return(proxies[:length])

print('Telegram channel - https://t.me/n4z4v0d\n')

config = dotenv_values('env.txt')
ANTICAPTCHA_KEY = str(config['CAPTCHA_API_KEY'])

threads = int(input('Threads: '))
emails_directory = str(input('Drop .txt with emails: '))

with open(emails_directory, 'r') as file:
	emails_list = [row.strip() for row in file]
	proxies = [None for _ in range(len(emails_list))]

use_proxy = str(input('Use Proxies? (y/N): ')).lower()

if use_proxy == 'y':
	proxy_source = int(input('How take proxies? (1 - tor proxies; 2 - from file): '))

	if proxy_source == 2:
		proxy_type = str(input('Enter proxy type (http; https; socks4; socks5): '))
		proxy_folder = str(input('Drag and drop file with proxies (ip:port; user:pass@ip:port): '))

		proxies = take_proxies(len(emails_list))


def mainth(data):
	for _ in range(100):
		try:
			wallet_data = create_wallet()
			email = data[0]
			proxy = data[1]

			session = Session()
			session.headers.update({'user-agent': random_useragent(), 'accept': 'application/json, text/javascript, */*; q=0.01', 'accept-language': 'ru,en;q=0.9,vi;q=0.8,es;q=0.7', 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8', 'origin': 'https://whitelist.nft.com', 'referer': 'https://whitelist.nft.com/'})

			if use_proxy == 'y':
				if proxy_source == 2:
					session.proxies.update({'http': f'{proxy_type}://{proxy}', 'https': f'{proxy_type}://{proxy}'})

				else:
					session.proxies.update(random_tor_proxy())

			while True:
				try:
					logger.info(f'{email} | Trying to solve a captcha')
					capmonster = RecaptchaV2Task(ANTICAPTCHA_KEY)
					task_id = capmonster.create_task('https://whitelist.nft.com/', '6Ld_PDofAAAAAGgWCpObjz92TbUHW39NkciR-IvR')
					result = capmonster.join_task_result(task_id)
					captcha_response = result.get("gRecaptchaResponse")
				except CapmonsterException as err:
					logger.error(f'Error when solving captcha for {email}: {str(err.error_code)}, trying again')

				except Exception as error:
					logger.error(f'Error when solving captcha for {email}: {str(error)}, trying again')
				else:
					logger.success(f'Captcha successfully solved for {email}')
					break

			r = session.post('https://webflow.com/api/v1/form/623c2701f0027da5946f9757', data = f'name=Signup+Form&source=https://whitelist.nft.com/&test=false&fields%5BEmail%5D{email}&fields%5Bethaddress%5D={wallet_data[0]}&fields%5Bg-recaptcha-response%5D={captcha_response}&dolphin=false')
			
			if '{"msg":"ok","code":200}' not in r.text:
				raise Wrong_Response(r)
		
		except Exception as error:
			logger.error(f'{email} | Unexpected error : {str(error)}')

		except Wrong_Response as error:
			logger.error(f'{email} | Wrong response: {str(error)}, response code: {str(r.status_code)}, response: {str(r.text)}')

		else:
			with open('registered.txt', 'a') as file:
				file.write(f'{email}:{wallet_data[0]}:{wallet_data[1]}\n')

			logger.success(f'{email} | Successfully registered')

			return

	with open('unregistered.txt', 'a') as file:
		file.write(f'{email}\n')


if __name__ == '__main__':
	clear()
	pool = Pool(threads)
	result_list = pool.map(mainth, list(zip(emails_list, proxies)))

	logger.success('Работа успешно завершена!')
	print('\nPress Any Key To Exit..')
	getch()
	exit()
