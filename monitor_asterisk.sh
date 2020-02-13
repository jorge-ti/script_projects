# ---
# Created by: Jorge
# Cxlagged: 09/10/2019
# Update: 11/10/2019
# Descrição: Registra todo estado atual do SIP
# Deve Ser utilizado no SIP

#-----------------------------------------

#--- Selecao de cores
COLOR_REST='\e[0m'       #  ${COLOR_REST}
COLOR_YELLOW='\e[0;33m'  #  ${COLOR_YELLOW}
COLOR_BLUE='\e[0;36m'    #  ${COLOR_BLUE}

#--- Formato de data e hora
cxv_data=`date +%d-%m-%y--%R`
cxv_data_full=`date +%d-%m-%Y' as '%R:%S`

#--- Captura ip/hostname da sessao 
cxv_tty=`tty | cut -d/ --complement -f1-2`
cxv_ip=`w | fgrep ${cxv_tty}`

#--- Define local aonde será salvo o log
cxv_local=/home/cx_verifica_sip.log

#--- local temporário -- não mexer
cxv_local_tmp=/tmp/cx_verifica_sip_tmp.log

#--- inicio
echo -e "${COLOR_YELLOW} ############### DATA NOVA CONSULTA ################# ${COLOR_REST}" >> ${cxv_local_tmp}
	
	echo "Inicio da nova verificacao em ${cxv_data_full} Por:" >> ${cxv_local_tmp}
	echo ' ' >> ${cxv_local_tmp}
	w | grep TTY >> ${cxv_local_tmp}
	echo ${cxv_ip} >> ${cxv_local_tmp}

echo ' ' >> ${cxv_local_tmp}
echo -e "${COLOR_BLUE} ############### TEMPO ATIVO DO SERVIDOR #################  ${COLOR_REST}" >> ${cxv_local_tmp}

	uptime | cut -d' ' -f3-5  | sed 's/,//g'>> ${cxv_local_tmp}

echo ' ' >> ${cxv_local_tmp}
echo -e "${COLOR_BLUE} ############### PROCESSAMENTO #################  ${COLOR_REST}" >> ${cxv_local_tmp}

	uptime | cut -d, -f4-6 >> ${cxv_local_tmp}

echo ' ' >> ${cxv_local_tmp}
echo -e "${COLOR_BLUE} ############### MEMORIA ####################### ${COLOR_REST}" >> ${cxv_local_tmp}

	free -hgt >> ${cxv_local_tmp}
 
echo ' ' >> ${cxv_local_tmp}
echo -e "${COLOR_BLUE} ############### ESPAÇO EM DISCO ############### ${COLOR_REST}" >> ${cxv_local_tmp}

	timeout 3 df -h >> ${cxv_local_tmp}
 
echo ' ' >> ${cxv_local_tmp}
echo -e "${COLOR_BLUE} ############### INODE ######################## ${COLOR_REST}" >> ${cxv_local_tmp}

	timeout 3 df -ih >> ${cxv_local_tmp}

echo ' '  >> ${cxv_local_tmp}
echo -e "${COLOR_BLUE} ############### ASTERISK -- TEMPO ATIVO ######################## ${COLOR_REST}" >> ${cxv_local_tmp}

	/usr/sbin/asterisk -rx 'core show uptime' >> ${cxv_local_tmp} 

echo ' ' >> ${cxv_local_tmp}
echo -e "${COLOR_BLUE} ############### ASTERISK -- ENTROCAMENTOS ######################## ${COLOR_REST}" >> ${cxv_local_tmp}

	/usr/sbin/asterisk -rx 'sip show peers' | egrep '5060|5061'  >> ${cxv_local_tmp} 


#--- printa na tela e salva o log 
more ${cxv_local_tmp}
sed -i "s/^/[${cxv_data}] /g" ${cxv_local_tmp}
cat ${cxv_local_tmp} >> ${cxv_local}
rm ${cxv_local_tmp}

#---
