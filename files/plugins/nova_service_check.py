#!/usr/bin/env python

# Copyright 2014, Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse

from maas_common import get_openstack_conn
from maas_common import metric_bool
from maas_common import print_output
from maas_common import status_err
from maas_common import status_ok


def check(args):
    try:
        conn = get_openstack_conn()
    # Catch any exception
    except Exception as e:
        status_err(str(e))

    # gather nova service states
    if args.host:
        services = [service for service in conn.compute.services 
                    if service.host == args.host]
    else:
        services = conn.compute.services()

    if len(services) == 0:
        status_err("No host(s) found in the service list")

    # return all the things
    status_ok()
    for service in services:
        service_is_up = True

        if service.status == 'enabled' and service.state == 'down':
            service_is_up = False

        if args.host:
            name = '%s_status' % service.binary
        else:
            name = '%s_on_host_%s_status' % (service.binary, service.host)

        metric_bool(name, service_is_up)


def main(args):
    check(args)


if __name__ == "__main__":
    with print_output():
        parser = argparse.ArgumentParser(description='Check nova services')
        parser.add_argument('--host',
                            type=str,
                            help='Only return metrics for specified host',
                            default=None)
        args = parser.parse_args()

        main(args)
