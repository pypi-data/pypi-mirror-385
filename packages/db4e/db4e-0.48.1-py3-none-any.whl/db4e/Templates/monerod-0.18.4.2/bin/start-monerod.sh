#!/bin/bash
#
# <vendor-dir>/bin/start-monerod.sh
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi 
#    Copyright: (c) 2024-2025 NadimGhaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0
#
# Script to start the Monero Blockchain daemon
#
#####################################################################

# Read in the settings
CONFIG_FILE="$1"

if [ -z $CONFIG_FILE ]; then
    echo "Usage $0 <INI file>"
    exit 1
fi 

source $CONFIG_FILE


# Don't allocate large pages
export MONERO_RANDOMX_UMASK=1

# Find the monerod daemon
if [ -d ${MONEROD_DIR} ]; then
	MONERO_DIR=$MONEROD_DIR
	MONEROD=${MONEROD_DIR}/bin/monerod
	if [ ! -x ${MONEROD} ]; then
		echo "ERROR: Unable to locate the monerod daemon (${MONEROD}), exiting..."
		exit 1
	fi
else
	echo "ERROR: Unable to locate the Monero software directory (${MONERO_DIR}), exiting..."
	exit 1
fi

# Make sure the blockchain directory exists
if [ ! -d ${BLOCKCHAIN_DIR} ]; then
	mkdir -p ${BLOCKCHAIN_DIR}
	if [ $? != 0 ]; then
		echo "ERROR: Failed to create blockchain data directory (${BLOCKCHAIN_DIR}), exiting..."
		exit 1
	fi
fi

# Launch the monerod daemon
$MONEROD \
	--log-level ${LOG_LEVEL} \
	--max-log-files ${MAX_LOG_FILES} \
	--max-log-file-size ${MAX_LOG_SIZE} \
	--log-file ${LOG_FILE} \
	--zmq-pub tcp://${IP_ALL}:${ZMQ_PUB_PORT} \
	--zmq-rpc-bind-ip ${IP_ALL} --zmq-rpc-bind-port ${ZMQ_RPC_PORT} \
	--p2p-bind-ip ${IP_ALL} --p2p-bind-port ${P2P_BIND_PORT} \
	--add-priority-node=${PRIORITY_NODE_1}:${PRIORITY_NODE_1_PORT} \
	--add-priority-node=${PRIORITY_NODE_2}:${PRIORITY_NODE_2_PORT} \
	--rpc-bind-ip ${IP_ALL} --rpc-bind-port ${RPC_BIND_PORT} --restricted-rpc \
	--confirm-external-bind \
	--data-dir ${BLOCKCHAIN_DIR} \
	--out-peers ${OUT_PEERS} \
	--in-peers ${IN_PEERS} \
	--disable-dns-checkpoints --enable-dns-blocklist \
	--show-time-stats ${SHOW_TIME_STATS} \
	--igd enabled \
	--max-connections-per-ip 1 \
	--db-sync-mode safe 