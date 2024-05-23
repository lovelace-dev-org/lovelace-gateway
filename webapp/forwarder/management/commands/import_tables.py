import json
from django.core.management.base import BaseCommand
import forwarder.models as fm

class Command(BaseCommand):
    help = "Imports student registry and hosts"

    def add_arguments(self, parser):
        parser.add_argument(
            "registry",
            help="Path of the student registry file"
        )
        parser.add_argument(
            "--hostfile",
            help="Path of the hosts file"
        )

    def handle(self, *args, **options):
        with open(options["registry"]) as registry:
            students = json.load(registry)

        with open(options["hostfile"]) as hostfile:
            hosts = [host.strip() for host in hostfile.readlines() if host]

        for i, student in enumerate(students):
            record = fm.ForwardMapping(
                **student
            )
            record.target_host = hosts[i % len(hosts)]
            record.save()





