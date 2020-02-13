#!/usr/bin/python 
#coding: utf-8
#-----------------------------------------
# Name: cxv_server
# Created by: Jorge Silva
# Made in: 30/10/2019
# Update: 19/11/2019
# Descricao: Registra todo estado atual servidor e gera um arquivo JSON
# Crontab: * * * * * /usr/bin/python /home/extend/scripts/cxv_server.py
#__________________________________________

import os
import sys
import commands
import json
import platform
from datetime import datetime

#--------------------------------------------------------

#--- Formato de data e hora
now = datetime.now()
hora = str(now.hour) + ":" + str(now.minute) + ":" + str(now.second)
data_single = str(now.day) + "-" + str(now.month) + "-" + str(now.year)
data_full = str(now.day) + "-" + str(now.month) + "-" + str(now.year) + "--" + str(now.hour) + "-" + str(now.minute) + "-" + str(now.second)

#--- Dicionarios para Dump JSON
cxv_json = {}
cxv_json_server = {}
cxv_json_pbx = {}
cxv_json_khomp = {}
cxv_json_trata = {}

#--- Metedo cria json
def gera_json(nome_json,path_json,data_json):
	file_path_name_json = path_json + nome_json + '.json'
	with open(file_path_name_json, 'w') as fp:
		json.dump(data_json, fp)

#--- Metodo apaga arquivo
def del_file(arquivo):
	if os.path.isfile(arquivo) == True:
		os.remove(arquivo)

#--- Nome e local do json
json_nome = 'cxv_server-' + data_full 
json_caminho = '/home/jorge/'
#json_caminho = os.environ['PWD'] + '/' 

#--- local temporário -- não mexer
py_cxv_local_job_tmp = '/tmp/.cxv_job_tmp'

#--------------------------------------------------------

#--- Inicio

del_file(py_cxv_local_job_tmp)

#--- --- ---  DATA NOVA CONSULTA 

cxv_json['data_json'] = {'data':data_single,
                         'hora':hora
                        } 


#-----------  SERVIDOR -----------

#--- --- ---  SERVER INFO //  TEMPO ATIVO DO SERVIDOR

py_cxv_uptime = commands.getoutput('uptime | cut -d" " -f4-5  | sed "s/,//g"')
py_cxv_model_processador = commands.getoutput('cat /proc/cpuinfo | grep "model name" | cut -d: -f2 | sort -u')
py_cxv_qtd_processador = commands.getoutput('nproc')
py_cxv_info_ip = commands.getoutput('hostname -I')
py_cxv_info_name = commands.getoutput('hostname')
py_cxv_info_os_release = platform.dist()[0] + ' - ' + platform.dist()[1] 
py_cxv_info_arquitetura = platform.architecture()[0]
py_cxv_info_time_zone = commands.getoutput('cat /etc/timezone')

if os.path.isfile('/etc/motd') == True:
	py_cxv_nome_server = commands.getoutput('cat /etc/motd  | grep - | sed s/#//g | cut -d- -f1')
else:
	py_cxv_nome_server = 'nao_possui'	

if os.path.isfile('/home/extend/comunix.conf') == True:
	py_cxv_nome_cliente = commands.getoutput('cat /home/extend/comunix.conf  | grep client_name | cut -d= -f2')
else:
	py_cxv_nome_cliente = 'nao_possui'	

cxv_json_server['server_info'] = {'server_ip':py_cxv_info_ip,
                                  'server_hostname':py_cxv_info_name, 
                                  'server_os_version':py_cxv_info_os_release, 
                                  'server_arquitetura':py_cxv_info_arquitetura,
                                  'server_uptime':py_cxv_uptime.replace("up  ",""),	
                                  'server_processador':py_cxv_model_processador.strip(), 
                                  'server_qtd_nucleo':py_cxv_qtd_processador,
                                  'server_nome_cliente':py_cxv_nome_cliente.replace(';',''), 
                                  'server_nome_server':py_cxv_nome_server.strip(),
                                  'server_time_zone':py_cxv_info_time_zone.strip()                                          

                                 }


#--- --- ---  PROCESSAMENTO

py_cxv_processamento = commands.getoutput('cat /proc/loadavg')

cxv_processamento = py_cxv_processamento.split()

cxv_json_server['processamento'] = {'01_minuto': cxv_processamento[0], 
                                    '05_minuto': cxv_processamento[1], 
                                    '15_minuto': cxv_processamento[2]
                                   }


#--- --- ---  MEMORIA 

py_cxv_memoria = commands.getoutput('free -hgt')

py_put_command = open(py_cxv_local_job_tmp, "a")
py_put_command.write(py_cxv_memoria)
py_put_command.close()

cxv_lista_memoria = []
with open(py_cxv_local_job_tmp, 'r') as data:
	next(data)
	for line in data:
		item = line.split()
		if 'buffers/cache' in line:
			None
		else:
			b = str(item[1].strip()) # total
			c = str(item[2].strip()) # usado
			d = str(item[3].strip()) # livre
			cxv_lista_memoria.append(b)
			cxv_lista_memoria.append(c)
			cxv_lista_memoria.append(d)

cxv_json_server['memoria'] = {'mem_total':cxv_lista_memoria[0],
                              'mem_usado':cxv_lista_memoria[1], 
                              'mem_livre':cxv_lista_memoria[2],
                              'mem_swap_total':cxv_lista_memoria[3],
                              'mem_swap_usado':cxv_lista_memoria[4],
                              'mem_swap_livre':cxv_lista_memoria[5],
                             }

del_file(py_cxv_local_job_tmp)


#--- --- ---  ESPACO EM DISCO

py_cxv_espaco_disco = commands.getoutput('timeout 3 df -h')

if py_cxv_espaco_disco == '':
	cxv_json_server['espaco_disco'] = 'timeout'	
else:
	py_put_command = open(py_cxv_local_job_tmp, "a")
	py_put_command.write(py_cxv_espaco_disco)
	py_put_command.close()

	cxv_lista_df_h = []
	with open(py_cxv_local_job_tmp, 'r') as data:
		next(data)
		for line in data:
			total = {}
			item = line.split()
			a = str(item[0].strip()) # nome_fs
			b = str(item[1].strip()) # total
			c = str(item[2].strip()) # usado
			d = str(item[3].strip()) # livre
			e = str(item[4].strip()) # porcentagem
			f = str(item[5].strip()) # montado_em 
			total.update({'nome_fs':a})
			total.update({'total': b})
			total.update({'usado': c})
			total.update({'livre': d})
			total.update({'porcentagem': e})
			total.update({'montado_em': f})
			cxv_lista_df_h.append(total)

	cxv_json_server['espaco_disco'] = cxv_lista_df_h

	del_file(py_cxv_local_job_tmp)


#--- --- ---  INODE

py_cxv_inode = commands.getoutput('timeout 3 df -ih')

if py_cxv_inode == '':
	cxv_json_server['inode'] = 'timeout'
else:
	py_put_command = open(py_cxv_local_job_tmp, "a")
	py_put_command.write(py_cxv_inode)
	py_put_command.close()

	cxv_lista_df_i = []
	with open(py_cxv_local_job_tmp, 'r') as data:
		next(data)
		for line in data:
			total={}
			item = line.split()
			a = str(item[0].strip()) # nome_fs
			b = str(item[1].strip()) # total
			c = str(item[2].strip()) # usado  
			d = str(item[3].strip()) # livre
			e = str(item[4].strip()) # porcentagem
			f = str(item[5].strip()) # montado_em
			total.update({'inode_nome_fs':a})      
			total.update({'inode_total': b})
			total.update({'inode_usado': c})
			total.update({'inode_livre': d})
			total.update({'inode_porcentagem': e})
			total.update({'inode_montado_em': f})
			cxv_lista_df_i.append(total)

	cxv_json_server['inode'] = cxv_lista_df_i

	del_file(py_cxv_local_job_tmp)


#--- --- --- TRATA

py_cxv_trata_proc = commands.getoutput('timeout 2 /home/extend/./trata_proc -v 2>/dev/null | grep Version | cut -d" " -f2,3')
py_cxv_trata_time_client = commands.getoutput('timeout 2 /home/extend/./trata_time_client -v 2>/dev/null | grep Version | cut -d" " -f2,3')
py_cxv_trata_tr_agente = commands.getoutput('timeout 2/home/extend/./trata_tr_agente_servico -v 2>/dev/null | grep Version | cut -d" " -f2,3')
py_cxv_trata_send_bilhete = commands.getoutput('timeout 2 /home/extend/./trata_send_bilhete_tcp -v 2>/dev/null | grep Version | cut -d" " -f2,3')
py_cxv_trata_fila = commands.getoutput('timeout 2 /home/extend/./trata_fila -v 2>/dev/null | grep Version | cut -d" " -f2,3')
py_cxv_trata_estatistica = commands.getoutput('timeout 2 /home/extend/./trata_estatistica -v 2>/dev/null | grep Version | cut -d" " -f2,3')
py_cxv_trata_bilhete = commands.getoutput('timeout 2 /home/extend/./trata_bilhetes -v 2>/dev/null | grep Version | cut -d" " -f2,3')
py_cxv_trata_heartbeat = commands.getoutput('timeout 2 /home/extend/./trata_heartbeat -v 2>/dev/null | grep Version | cut -d" " -f2,3')
py_cxv_trata_time_server = commands.getoutput('timeout 2 /home/extend/./trata_time_server -v 2>/dev/null  | grep Version | cut -d" " -f2,3')
py_cxv_trata_call = commands.getoutput('timeout 2 /home/extend/./trata_call -v 2>/dev/null | grep Version | cut -d" " -f2,3')

if py_cxv_trata_proc == '':
	py_cxv_trata_proc = 'nao_possui'
if py_cxv_trata_time_client == '':
	py_cxv_trata_time_client = 'nao_possui'
if py_cxv_trata_tr_agente == '':
	py_cxv_trata_tr_agente = 'nao_possui'
if py_cxv_trata_send_bilhete == '':
	py_cxv_trata_send_bilhete = 'nao_possui'
if py_cxv_trata_fila == '':
	py_cxv_trata_fila = 'nao_possui'
if py_cxv_trata_estatistica == '':
	py_cxv_trata_estatistica = 'nao_possui'
if py_cxv_trata_bilhete == '':
	py_cxv_trata_bilhete = 'nao_possui'
if py_cxv_trata_heartbeat == '':
	py_cxv_trata_heartbeat = 'nao_possui'
if py_cxv_trata_time_server == '':
	py_cxv_trata_time_server = 'nao_possui'
if py_cxv_trata_call == '':
	py_cxv_trata_call = 'nao_possui'

cxv_json_trata['trata_version'] = {'trata_proc':py_cxv_trata_proc,
                                    'trata_time_client':py_cxv_trata_time_client,
                                    'trata_tr_agente':py_cxv_trata_tr_agente,
                                    'trata_send_bilhete':py_cxv_trata_send_bilhete,
                                    'trata_fila':py_cxv_trata_fila,
                                    'trata_estatistica':py_cxv_trata_estatistica,
                                    'trata_bilhete':py_cxv_trata_bilhete,
                                    'trata_heartbeat':py_cxv_trata_heartbeat,
                                    'trata_time_server':py_cxv_trata_time_server,
                                    'trata_call':py_cxv_trata_call
                                    }


#--- --- --- TRATA STATUS 

py_cxv_status_trata_proc = commands.getoutput('ps axu | grep "/home/extend/./trata_proc" | grep -v grep')
py_cxv_status_trata_time_client = commands.getoutput('ps axu | grep  "/home/extend/./trata_time_client" | grep -v grep')
py_cxv_status_trata_tr_agente = commands.getoutput('ps axu | grep "/home/extend/./trata_tr_agente_servico" | grep -v grep')
py_cxv_status_trata_send_bilhete = commands.getoutput('ps axu | grep "/home/extend/./trata_send_bilhete_tcp" | grep -v grep')
py_cxv_status_trata_fila = commands.getoutput('ps axu | grep "/home/extend/./trata_fila" | grep -v grep')
py_cxv_status_trata_estatistica = commands.getoutput('ps axu | grep "/home/extend/./trata_estatistica" | grep -v grep')
py_cxv_status_trata_bilhete = commands.getoutput('ps axu | grep "/home/extend/./trata_bilhetes" | grep -v grep')
py_cxv_status_trata_heartbeat = commands.getoutput('ps axu | grep "/home/extend/./trata_heartbeat" | grep -v grep')
py_cxv_status_trata_time_server = commands.getoutput('ps axu | grep "/home/extend/./trata_time_server" | grep -v grep')
py_cxv_status_trata_call = commands.getoutput('ps axu | grep "/home/extend/./trata_call" | grep -v grep')
py_cxv_status_share = commands.getoutput('ps aux | grep  "/home/extend/./trata_share" | grep -v grep')
py_cxv_status_trata_getcloudkey = commands.getoutput('ps aux | grep "/home/extend/./trata_getcloudkey" | grep -v grep')

if py_cxv_status_trata_proc != '':
	py_cxv_status_trata_proc = 'UP'
else:
	py_cxv_status_trata_proc = 'Down'	

if py_cxv_status_trata_time_client != '':
	py_cxv_status_trata_time_client = 'UP'
else: 
	py_cxv_status_trata_time_client = 'Down'

if py_cxv_status_trata_tr_agente != '':
	py_cxv_status_trata_tr_agente = 'UP'
else: 
	py_cxv_status_trata_tr_agente = 'Down'

if py_cxv_status_trata_send_bilhete != '':
	py_cxv_status_trata_send_bilhete = 'UP'
else:
	py_cxv_status_trata_send_bilhete = 'Down'

if py_cxv_status_trata_fila != '':
	py_cxv_status_trata_fila = 'UP'
else:
	py_cxv_status_trata_fila = 'Down'

if py_cxv_status_trata_estatistica != '':
	py_cxv_status_trata_estatistica = 'UP'
else:
	py_cxv_status_trata_estatistica = 'Down'

if py_cxv_status_trata_bilhete != '':
	py_cxv_status_trata_bilhete = 'UP'
else:
	py_cxv_status_trata_bilhete = 'Down'

if py_cxv_status_trata_heartbeat != '':
	py_cxv_status_trata_heartbeat = 'UP'
else:	
	py_cxv_status_trata_heartbeat = 'Down'

if py_cxv_status_trata_time_server != '':
	py_cxv_status_trata_time_server = 'UP'
else:
	py_cxv_status_trata_time_server = 'Down'

if  py_cxv_status_trata_call != '':
	py_cxv_status_trata_call = 'UP'
else: 
	py_cxv_status_trata_call = 'Down'

if py_cxv_status_share != '':
	py_cxv_status_share = 'UP'
else:
	py_cxv_status_share = 'Down'

if py_cxv_status_trata_getcloudkey != '':
	py_cxv_status_trata_getcloudkey = 'UP'
else:
	py_cxv_status_trata_getcloudkey = 'Down'

cxv_json_trata['trata_status'] = {'status_trata_proc':py_cxv_status_trata_proc,
                                   'status_trata_time_client':py_cxv_status_trata_time_client,
                                   'status_trata_tr_agente_servico':py_cxv_status_trata_tr_agente,
                                   'status_trata_send_bilhete':py_cxv_status_trata_send_bilhete,
                                   'status_trata_fila':py_cxv_status_trata_fila,
                                   'status_trata_estatistica':py_cxv_status_trata_estatistica,
                                   'status_trata_bilhete':py_cxv_status_trata_bilhete,
                                   'status_trata_heartbeat':py_cxv_status_trata_heartbeat,
                                   'status_trata_time_server':py_cxv_status_trata_time_server,
                                   'status_trata_call':py_cxv_status_trata_call,
                                   'status_trata_share':py_cxv_status_share, 
                                   'status_trata_getcloudkey':py_cxv_status_trata_getcloudkey
                                 }                               

cxv_json_server['trata'] = cxv_json_trata


#-----------  COMUNIX/ASTERISK  -----------

#--- --- --- STATUS COMUNIX/ASTERISK/KHOMP

py_cxv_chk_comunix = commands.getoutput('/usr/sbin/comunix -rx "core show uptime seconds"')   
py_cxv_chk_asterisk = commands.getoutput('/usr/sbin/asterisk -rx "core show uptime seconds"')
py_cxv_chk_khomp_comunix = commands.getoutput('/usr/sbin/comunix -rx "khomp summary" | grep -i Summary')
py_cxv_chk_khomp_asterisk = commands.getoutput('/usr/sbin/asterisk -rx "khomp summary" | grep -i Summary')

#--- variaveis de verificacao de status comunix/asterisk

py_cxv_comunix_status = None
py_cxv_asterisk_status = None
py_cxv_khomp_comunix_status = None
py_cxv_khomp_asterisk_status = None

if 'System uptime' in py_cxv_chk_comunix:
	py_cxv_comunix_status = 'UP'
else: 
	py_cxv_comunix_status = 'Down'

if 'System uptime' in py_cxv_chk_asterisk:
	py_cxv_asterisk_status = 'UP'
else: 	
	py_cxv_asterisk_status = 'Down'

if 'Khomp System Summary' in py_cxv_chk_khomp_comunix:
        py_cxv_khomp_comunix_status = 'UP'
else:
       	py_cxv_khomp_comunix_status = 'Down'

if 'Khomp System Summary' in py_cxv_chk_khomp_asterisk:
        py_cxv_khomp_asterisk_status = 'UP'
else:
        py_cxv_khomp_asterisk_status = 'Down'


cxv_json_pbx['pbx_status'] = {'status_comunix':py_cxv_comunix_status,
                              'status_asterisk':py_cxv_asterisk_status
                             }

cxv_json_khomp['khomp_status'] = {'status_khomp_comunix':py_cxv_khomp_comunix_status,
                                  'status_khomp_asterisk':py_cxv_khomp_asterisk_status
                                 }



#--- --- ---  STATUS PBX 

if py_cxv_comunix_status == 'Down' and py_cxv_asterisk_status == 'Down':
	None

else: 
	
#--- --- ---  PBX INFO

	if py_cxv_comunix_status == 'UP':
		py_cxv_pbx_version = commands.getoutput('/usr/sbin/comunix -rx "core show version" | sed s/" "/:/g')
	elif py_cxv_asterisk_status == 'UP':
		py_cxv_pbx_version = commands.getoutput('/usr/sbin/asterisk -rx "core show version" | sed s/" "/:/g')
	else:
		py_cxv_pbx_version = 'nenhum'

	cxv_pbx_tipo = None

	if py_cxv_comunix_status == 'Down' and py_cxv_asterisk_status == 'UP':
		cxv_pbx_tipo = 'asterisk'
	elif py_cxv_comunix_status == 'UP' and py_cxv_asterisk_status == 'Down':
		cxv_pbx_tipo = 'comunix'
	elif py_cxv_comunix_status == 'UP' and py_cxv_asterisk_status == 'UP':
		cxv_pbx_tipo = 'ambos'
	elif py_cxv_comunix_status == 'Down' and py_cxv_asterisk_status == 'Down':
		cxv_pbx_tipo = 'nenhum'

	cxv_json_pbx['pbx_info'] = {'running':cxv_pbx_tipo, 
	                            'core_version':py_cxv_pbx_version.split(':')[0] + ' ' + py_cxv_pbx_version.split(':')[1]
	                           }


#--- --- ---  TEMPO ATIVO COMUNIX/ASTERISK

	if py_cxv_comunix_status == 'UP':
		py_cxv_cx_uptime = commands.getoutput('/usr/sbin/comunix -rx "core show uptime seconds" | grep "System uptime" | cut -d: -f2')
	elif py_cxv_asterisk_status == 'UP':
		py_cxv_cx_uptime = commands.getoutput('/usr/sbin/asterisk -rx "core show uptime seconds" | grep "System uptime" | cut -d: -f2')

	cxv_cx_segundos = py_cxv_cx_uptime
	cxv_cx_total_segundos = int(cxv_cx_segundos)
	cxv_cx_horas = cxv_cx_total_segundos // 3600
	cxv_cx_dias = cxv_cx_horas // 86400
	cxv_cx_segs_restantes = cxv_cx_total_segundos % 3600
	cxv_cx_minutos = cxv_cx_segs_restantes // 60
	cxv_cx_segs_restantes_final = cxv_cx_segs_restantes % 60

	if (cxv_cx_horas >= 24): 
		cxv_cx_dias = int(cxv_cx_horas / 24)
		cxv_cx_horas = int(cxv_cx_horas % 24)
	
 	cxv_json_pbx['pbx_uptime'] = {'dias':cxv_cx_dias, 
 	                             'horas':cxv_cx_horas,
 	                              'minutos':cxv_cx_minutos,
 	                              'segundos':cxv_cx_segs_restantes_final
 	                             }


#--- --- ---  ENTRONCAMENTO

	if py_cxv_comunix_status == 'UP':
		py_cxv_entronca_sip = commands.getoutput('/usr/sbin/comunix -rx "sip show peers" | grep [5][0][6][0-1]')
	elif py_cxv_asterisk_status == 'UP':
		py_cxv_entronca_sip = commands.getoutput('/usr/sbin/asterisk -rx "sip show peers" | grep [5][0][6][0-1]')

	py_put_command = open(py_cxv_local_job_tmp, "a")
	py_put_command.write(py_cxv_entronca_sip)
	py_put_command.close()

	cxv_lista_entroncamento = []
	with open(py_cxv_local_job_tmp, 'r') as data:
		for line in data:
			total={}
			item = line.split()
			if 'Monitored:' in line:
				None
			else:
				a = str(item[0].strip())  # nome_entrocamento
				b = str(item[1].strip())  # hostname
				c = str(item[-1].strip()) # status
				if c == 'Unmonitored' or c == 'UNKNOWN' or c == 'UNREACHABLE':
					c = str(item[-1].strip())
				else: 
					c = str(item[-3].strip()) + str(item[-2]) + str(item[-1]) 
				total.update({'nome': a})
				total.update({'host': b})
				total.update({'status': c})
				cxv_lista_entroncamento.append(total)

	del_file(py_cxv_local_job_tmp)
	
	cxv_json_pbx['pbx_entroncamento'] = cxv_lista_entroncamento


#-----------  KHOMP   -----------

#--- --- --- SUMMARY
	
	if py_cxv_khomp_comunix_status == 'Down' and py_cxv_khomp_asterisk_status == 'Down':
		None
	
	else: 
		cxv_json_khomp_summary = {}
		
		if py_cxv_comunix_status == 'UP':
			py_cxv_khomp_summary = commands.getoutput('/usr/sbin/comunix -rx "khomp summary concise" | cut -d" " -f2')
		if py_cxv_asterisk_status == 'UP':
			py_cxv_khomp_summary = commands.getoutput('/usr/sbin/asterisk -rx "khomp summary concise" | cut -d" " -f2')	
		
		py_put_command = open(py_cxv_local_job_tmp, "a")
		py_put_command.write(py_cxv_khomp_summary)
		py_put_command.close()

		with open(py_cxv_local_job_tmp, 'r') as data:
			khomp_api = data.readline().split(';')[0]
			khomp_drive = data.readline().strip()
		
		cxv_lista_ebs = []
		with open(py_cxv_local_job_tmp, 'r') as data:
			next(data)
			next(data)	
			for line in data:
				total = {}
				item = line.split(';')
				cxv_khomp_tipo = None
				khomp_tipo = str(item[1]).split('-')[0]
				if 'EBS' in khomp_tipo:
					cxv_khomp_tipo = 'EBS'
				
					a = str(item[0].strip())  # board 
					b = str(item[1].strip())  # ebs
					c = str(item[2].strip())  # serial
					d = str(item[3].strip())  # canais
					e = str(item[5].strip())  # ip
					f = str(item[6].strip())  # status
					g = str(item[4].strip())  # mac
								 
					total.update({'board': a})
					total.update({'ebs_nome': b})
					total.update({'serial': c})
					total.update({'canais': d})
					total.update({'ip': e})
					total.update({'status': f.strip()})
					total.update({'mac': g.strip()})
					cxv_lista_ebs.append(total)

				else:
					cxv_khomp_tipo = 'PCI'

		cxv_json_khomp_summary.update({'tipo': cxv_khomp_tipo })
		cxv_json_khomp_summary.update({'ebs': cxv_lista_ebs})
		cxv_json_khomp_summary.update({'drive': khomp_drive})
		cxv_json_khomp_summary.update({'api': khomp_api})
		
		cxv_json_khomp['khomp_summary'] = cxv_json_khomp_summary

		del_file(py_cxv_local_job_tmp)


#--- --- --- LINK STATUS

		if py_cxv_comunix_status == 'UP':
			py_cxv_khomp_links_status = commands.getoutput('/usr/sbin/comunix -rx "khomp links show concise" | sed s/kes//')
		elif py_cxv_asterisk_status == 'UP':
			py_cxv_khomp_links_status = commands.getoutput('/usr/sbin/asterisk -rx "khomp links show concise" | sed s/kes//')	

		py_put_command = open(py_cxv_local_job_tmp, "a")
		py_put_command.write(py_cxv_khomp_links_status)
		py_put_command.close()
		
		cxv_lista_links_0 = []
		cxv_lista_links_1 = []
		cxv_lista_links_2 = []
		cxv_lista_links_3 = []
		cxv_lista_links_4 = []
		cxv_lista_links_5 = []
		cxv_lista_links_6 = []
		cxv_lista_links_7 = []	
	
		cxv_lista_khomp_links = []
		with open(py_cxv_local_job_tmp, 'r') as data:	
			for line in data:
				total = {}
				line = line.replace('L0',':L0')
				item = line.split(':')
				a = str(item[0].replace('B0','').strip()) #board
				b = str(item[1].replace('L0','').strip()) #links
				try:
					c = str(item[2].replace('{','').replace('}','').strip()) #status
				except (IndexError, ValueError):
					c = 'null'
				total.update({'board': a})
				total.update({'link': b})
				total.update({'status': c})
				y = str(item[0].replace('B0','').strip())
				if 'XX' in y:
					y = 1  
				x = int(y)
				
				if x == 0:
					cxv_lista_links_0.append(total)
				else:	
					if x ==1 :
						cxv_lista_links_1.append(total)
					else:
						if x == 2:
							cxv_lista_links_2.append(total)
						else:
							if x == 3:
								cxv_lista_links_3.append(total)
							else:		
								if x == 4:
									cxv_lista_links_4.append(total)
								else:
									if x == 5:
										cxv_lista_links_5.append(total)	
									else:
										if x == 6:
											cxv_lista_links_6.append(total)
										else:
											if x == 7:	
												cxv_lista_links_7.append(total)			
												
							
			if len(cxv_lista_links_0) != 0:
				cxv_lista_khomp_links.append(cxv_lista_links_0)
			if len(cxv_lista_links_1) != 0:
				cxv_lista_khomp_links.append(cxv_lista_links_1)
			if len(cxv_lista_links_2) != 0:
				cxv_lista_khomp_links.append(cxv_lista_links_2)
			if len(cxv_lista_links_3) != 0:
				cxv_lista_khomp_links.append(cxv_lista_links_3)
			if len(cxv_lista_links_4) != 0:
				cxv_lista_khomp_links.append(cxv_lista_links_4)
			if len(cxv_lista_links_5) != 0:
				cxv_lista_khomp_links.append(cxv_lista_links_5)
			if len(cxv_lista_links_6) != 0:
				cxv_lista_khomp_links.append(cxv_lista_links_6)
			if len(cxv_lista_links_7) != 0:
				cxv_lista_khomp_links.append(cxv_lista_links_7)
		


		cxv_json_khomp['khomp_link'] = cxv_lista_khomp_links 
		
		del_file(py_cxv_local_job_tmp)


#--- --- --- LINK ERROS

		if py_cxv_comunix_status == 'UP':
			py_cxv_khomp_links_errors = commands.getoutput('/usr/sbin/comunix -rx "khomp links errors concise" | cut -d" " -f 2 | sed s/klec//')
		elif py_cxv_asterisk_status == 'UP':
			py_cxv_khomp_links_errors = commands.getoutput('/usr/sbin/asterisk -rx "khomp links errors concise" | cut -d" " -f 2 | sed s/klec//')	

		py_put_command = open(py_cxv_local_job_tmp, "a")
		py_put_command.write(py_cxv_khomp_links_errors)
		py_put_command.close()
		
		cxv_lista_board_0 = []
		cxv_lista_board_1 = []
		cxv_lista_board_2 = []
		cxv_lista_board_3 = []
		cxv_lista_board_4 = []
		cxv_lista_board_5 = []
		cxv_lista_board_6 = []
		cxv_lista_board_7 = []

		cxv_lista_khomp_links_errors = []
		with open(py_cxv_local_job_tmp, 'r') as data:

			for line in data:
				total = {}
				item = line.split(':')
				a = str(item[0].strip()) #n board
				b = str(item[1].strip()) #link
				c = str(item[2].strip()) #boad
				d = str(item[3].strip()) #qtd_erros
				total.update({'board': a})
				total.update({'link': b})
				total.update({'error_name': c})
				total.update({'qtd_errors': d})
				x = int(a)

				if x == 0:
					cxv_lista_board_0.append(total)
				else:	
					if x ==1 :
						cxv_lista_board_1.append(total)
					else:
						if x == 2:
							cxv_lista_board_2.append(total)
						else:
							if x == 3:
								cxv_lista_board_3.append(total)
							else:		
								if x == 4:
									cxv_lista_board_4.append(total)
								else:
									if x == 5:
										cxv_lista_board_5.append(total)	
									else:
										if x == 6:
											cxv_lista_board_6.append(total)
										else:
											if x == 7:	
												cxv_lista_board_7.append(total)			
													
								
			if len(cxv_lista_board_0) != 0:
				cxv_lista_khomp_links_errors.append(cxv_lista_board_0)
			if len(cxv_lista_board_1) != 0:
				cxv_lista_khomp_links_errors.append(cxv_lista_board_1)
			if len(cxv_lista_board_2) != 0:
				cxv_lista_khomp_links_errors.append(cxv_lista_board_2)
			if len(cxv_lista_board_3) != 0:
				cxv_lista_khomp_links_errors.append(cxv_lista_board_3)
			if len(cxv_lista_board_4) != 0:
				cxv_lista_khomp_links_errors.append(cxv_lista_board_4)
			if len(cxv_lista_board_5) != 0:
				cxv_lista_khomp_links_errors.append(cxv_lista_board_5)
			if len(cxv_lista_board_6) != 0:
				cxv_lista_khomp_links_errors.append(cxv_lista_board_6)
			if len(cxv_lista_board_7) != 0:
				cxv_lista_khomp_links_errors.append(cxv_lista_board_7)

			cxv_json_khomp['khomp_errors'] = cxv_lista_khomp_links_errors	
			
			del_file(py_cxv_local_job_tmp)
		

#--- --- --- CHANNELS SHOW

		if py_cxv_comunix_status == 'UP':
			py_cxv_khomp_channel_show = commands.getoutput('/usr/sbin/comunix -rx "khomp channels show" | grep -v -  | grep -v asterisk | grep -v status | sed "s/<K> |//g"')
		elif py_cxv_asterisk_status == 'UP':
			py_cxv_khomp_channel_show = commands.getoutput('/usr/sbin/asterisk -rx "khomp channels show" | grep -v -  | grep -v asterisk | grep -v status | sed "s/<K> |//g"') 			


		py_put_command = open(py_cxv_local_job_tmp, "a")
		py_put_command.write(py_cxv_khomp_channel_show)
		py_put_command.close()

		cxv_lista_channel_show = []
		with open(py_cxv_local_job_tmp, 'r') as data:
			for line in data:
				total={}
				item = line.split("|")
				a = str(item[0].strip())  # canal/link
				b = str(item[1].strip())  # asterisk status
				c = str(item[2].strip())  # chamada status
				d = str(item[3].strip())  # canais status
				e = str(item[-2].strip())  # sinalizacao 
				total.update({'canal/link': a}) 
				total.update({'status-asterisk': b})
				total.update({'status-chamada': c})
				total.update({'status-canais': d})
				total.update({'sinalizacao': e})
				if 'GSM' in e: 
					f = str(item[-4].strip())  # status-sinal-gsm
					total.update({'status-gsm': f})

				cxv_lista_channel_show.append(total)

		del_file(py_cxv_local_job_tmp)
		
		cxv_json_khomp['khomp_channels'] = cxv_lista_channel_show

#--- Finalizacao dicionarios

cxv_json['khomp'] = cxv_json_khomp
cxv_json['pbx'] = cxv_json_pbx
cxv_json['servidor'] = cxv_json_server

#--- chama metodo gerar json

#print(json.dumps(cxv_json))
gera_json(json_nome,json_caminho,cxv_json)

#----------------------------------------------------------------------------------------
