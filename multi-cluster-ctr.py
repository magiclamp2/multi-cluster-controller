#!/usr/bin/python3
#please run this script at root level
import subprocess, socket, argparse, re, shlex, ssl

def main(mode, cluster):
    if mode == 'switch':
       interCluster(cluster)
    else:
       intraCluster(mode)


def intraCluster(mode):
    if ( mode == 'info' ):
      path = "/etc/kubernetes/kubelet.conf"
      try:
          with open(path,'r') as myfile:
              lines = myfile.readlines()
              for line in lines:
                  if re.search(r'server', line):
                      print("Current cluster {}".format(line.lstrip()))
                      break
      except FileNotFoundError as e:
          print("No cluster is participating currently")
    elif ( mode == 'scheduleOff'):
      cmd = "systemctl stop kubelet"
      print(cmd)
      out=subprocess.check_output(shlex.split(cmd), universal_newlines=True)
      print(out)

    elif ( mode == 'suspend'):
      cmd = ["systemctl stop kubelet", "systemctl restart docker"]
      for command in cmd:
          out=subprocess.check_output(shlex.split(command), universal_newlines=True)
          print("{} it is suspended successfully".format(out))

    elif ( mode == 'resume' ):
      cmd = "systemctl start kubelet"
      print(cmd)
      out=subprocess.check_output(shlex.split(cmd), universal_newlines=True)
      print(out)

    elif ( mode == 'terminate' ):
      cmd = "kubeadm reset -f"
      print(cmd)
      out=subprocess.check_output(shlex.split(cmd), universal_newlines=True)
      print(out)

def interCluster(cluster):
    reset_cmd = "kubeadm reset -f"
    print(reset_cmd)
    out=subprocess.check_output(shlex.split(reset_cmd), universal_newlines=True)
    print(out)
    join_cmd = runClient(cluster)
    print(join_cmd)
    out=subprocess.check_output(shlex.split(join_cmd), universal_newlines=True)
    print(out)


def runClient(cluster):
    if cluster == 'minidtn4':
        HOST = ""
        PORT = 
        server_sni_hostname = 'minidtn4'
        kubeconfig = '/home/k8s/.kube/config'
        server_cert = '/home/k8s/multi-ctr/server.crt'
        client_cert = '/home/xiao/.kube/minidtn3.crt'
        client_key = '/home/xiao/.kube/minidtn3.key'
    elif cluster == 'minidtn5':
        HOST = ""
        PORT = 
        server_sni_hostname = 'minidtn5'
        kubeconfig = ''
        server_cert = '/home/k8s/multi-ctr/server.cert'
        client_cert = '/home/k8s/multi-ctr/client3.crt'
        client_key = '/home/k8s/multi-ctr/client3np.key'

    if kubeconfig:
        join_cmd = "kubeadm join --discovery-file kubeconfig"
    else:
        print("B")
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_cert)
        context.load_cert_chain(certfile=client_cert, keyfile=client_key)
        context.check_hostname = True
        
        s = socket.socket(socket.AF_INET,   socket.SOCK_STREAM)
        ssl_sock = context.wrap_socket(s, server_side=False, server_hostname=server_sni_hostname)
        ssl_sock.connect((HOST, PORT))
        print("[+] Connected with Server")
        print("SSL established. Peer: {}".format(ssl_sock.getpeercert()))
        print("[+] Sending cmd...")
        ssl_sock.sendall(b'request-join-command')

        print('[-] Finished sending')
        ssl_sock.send(b'//stop')
        print('[+] Receving join command')
        while True:
            data = ssl_sock.recv(4096)
            if data.startswith(b'kubeadm'):
                join_cmd = data.decode()
            elif not data:
               break
        ssl_sock.close()
        print("[-] Finished")
    return join_cmd

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", help="action: cluster-info; suspend; resume; switch", type=str, default='info')
    parser.add_argument("--cluster", help="cluster to switch over", type=str)

    args = parser.parse_args()

    main(args.mode, args.cluster)
