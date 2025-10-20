import argparse
import yaml
import os 
import socket
import paramiko
import dns.resolver
import base64


def get_cloud_domain(target_pve):
  with open(os.path.expanduser("~/.pve-cloud-dyn-inv.yaml"), "r") as f:
    pve_inventory = yaml.safe_load(f)

  for pve_cloud in pve_inventory:
    for pve_cluster in pve_inventory[pve_cloud]:
      if pve_cluster + "." + pve_cloud == target_pve:
        return pve_cloud
  
  raise Exception(f"Could not identify cloud domain for {target_pve}")


def get_cld_domain_prsr(args):
  print(f"export PVE_CLOUD_DOMAIN='{get_cloud_domain(args.target_pve)}'")


def get_online_pve_host(target_pve):
  with open(os.path.expanduser("~/.pve-cloud-dyn-inv.yaml"), "r") as f:
    pve_inventory = yaml.safe_load(f)

  for pve_cloud in pve_inventory:
    for pve_cluster in pve_inventory[pve_cloud]:
      if pve_cluster + "." + pve_cloud == target_pve:
        for pve_host in pve_inventory[pve_cloud][pve_cluster]:
          # check if host is available
          pve_host_ip = pve_inventory[pve_cloud][pve_cluster][pve_host]["ansible_host"]
          try:
              with socket.create_connection((pve_host_ip, 22), timeout=3):
                  return pve_host_ip
          except Exception as e:
              # debug
              print(e, type(e))
              pass
  
  raise Exception(f"Could not find online pve host for {target_pve}")


def get_cloud_env(pve_host):
  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

  ssh.connect(pve_host, username="root")

  # since we need root we cant use sftp and root via ssh is disabled
  _, stdout, _ = ssh.exec_command("cat /etc/pve/cloud/cluster_vars.yaml")

  cluster_vars = yaml.safe_load(stdout.read().decode('utf-8'))

  _, stdout, _ = ssh.exec_command("cat /etc/pve/cloud/secrets/patroni.pass")

  patroni_pass = stdout.read().decode('utf-8')

  return cluster_vars, patroni_pass


def get_online_pve_host_prsr(args):
  print(f"export PVE_ANSIBLE_HOST='{get_online_pve_host(args.target_pve)}'")


def get_ssh_master_kubeconfig(cluster_vars, stack_name):
  resolver = dns.resolver.Resolver()
  resolver.nameservers = [cluster_vars['bind_master_ip'], cluster_vars['bind_slave_ip']]

  ddns_answer = resolver.resolve(f"masters-{stack_name}.{cluster_vars['pve_cloud_domain']}")
  ddns_ips = [rdata.to_text() for rdata in ddns_answer]

  if not ddns_ips:
    raise Exception("No master could be found via DNS!")

  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

  ssh.connect(ddns_ips[0], username="admin")

  # since we need root we cant use sftp and root via ssh is disabled
  _, stdout, _ = ssh.exec_command("sudo cat /etc/kubernetes/admin.conf")

  return base64.b64encode(stdout.read().decode('utf-8').replace("https://127.0.0.1:6443", f"https://{ddns_ips[0]}:6443").encode('utf-8')).decode('utf-8')


def export_envr(args):
  ansible_host = get_online_pve_host(args.target_pve)
  cloud_domain = get_cloud_domain(args.target_pve)
  cluster_vars, patroni_pass = get_cloud_env(ansible_host)
  print(f"export PVE_ANSIBLE_HOST='{ansible_host}'")
  print(f"export PVE_CLOUD_DOMAIN='{cloud_domain}'")

  # tf vars
  print(f"export PG_CONN_STR=\"postgres://postgres:{patroni_pass}@{cluster_vars['pve_haproxy_floating_ip_internal']}:5000/tf_states?sslmode=disable\"")
  print(f"export TF_VAR_pve_cloud_domain='{cloud_domain}'")
  print(f"export TF_VAR_pve_host='{ansible_host}'")
  print(f"export TF_VAR_cluster_proxy_ip='{cluster_vars['pve_haproxy_floating_ip_internal']}'")
  print(f"export TF_VAR_pve_cloud_pg_cstr=\"postgresql+psycopg2://postgres:{patroni_pass}@{cluster_vars['pve_haproxy_floating_ip_internal']}:5000/pve_cloud?sslmode=disable\"")
  print(f"export TF_VAR_master_b64_kubeconf='{get_ssh_master_kubeconfig(cluster_vars, args.stack_name)}'")


  
def main():
  parser = argparse.ArgumentParser(description="PVE Cloud utility cli. Should be called with bash eval.")

  base_parser = argparse.ArgumentParser(add_help=False)

  subparsers = parser.add_subparsers(dest="command", required=True)

  get_cld_domain_parser = subparsers.add_parser("get-cloud-domain", help="Get the cloud domain of a pve cluster.", parents=[base_parser])
  get_cld_domain_parser.add_argument("--target-pve", type=str, help="The target pve cluster to get the cloud domain of.", required=True)
  get_cld_domain_parser .set_defaults(func=get_cld_domain_prsr)

  export_envr_parser = subparsers.add_parser("export-envrc", help="Export variables for k8s .envrc", parents=[base_parser])
  export_envr_parser.add_argument("--target-pve", type=str, help="The target pve cluster.", required=True)
  export_envr_parser.add_argument("--stack-name", type=str, help="Stack name of the deployment.", required=True)
  export_envr_parser.set_defaults(func=export_envr)

  get_online_pve_host_parser = subparsers.add_parser("get-online-host", help="Gets the ip for the first online proxmox host in the cluster.", parents=[base_parser])
  get_online_pve_host_parser.add_argument("--target-pve", type=str, help="The target pve cluster to get the first online ip of.", required=True)
  get_online_pve_host_parser.set_defaults(func=get_online_pve_host_prsr)

  args = parser.parse_args()
  args.func(args)


if __name__ == "__main__":
  main()