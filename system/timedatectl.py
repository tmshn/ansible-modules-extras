#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2016, Shinichi TAMURA (@tmshn)
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

import re

DOCUMENTATION = '''
---
module: timedatectl
short_description: Execute `timedatectl` command to set timezone, etc
description:
  - Execute `timedatectl` command to set timezone, date/time or enable NTP.
  - See `man timedatectl` for details.
version_added: "2.1.0"
options:
  ntp:
    description:
      - Enable/Disable clock synchronization using NTP.
      - Default is to keep current setting.
    required: false
    choices: [ "yes", "no" ]
    default: null
  time:
    description:
      - Set current date and/or time of the system clock, specified in the format I(2012-10-30 18:17:16).
      - Default is to keep current setting.
    required: false
    default: null
  timezone:
    description:
      - Set time zone of the system clock, specified in the format I(Asia/Tokyo).
      - Default is to keep current setting.
    required: false
    default: null
requirements: [ "timedatectl command" ]
author: "Shinichi TAMURA @tmshn"
'''

RETURN = '''
changelogs:
  description: The change logs concerning to the given arguments.
  returned: success
  type: list of dictionary
  contains:
    name:
      description: The name of the column
      type: string
    old_value:
      description: The value before task is executed
      type: string
    new_value:
      description: The value after task is executed
      type: string
    command:
      description: The command executed
      type: string
    changed:
      description: If change happend
      type: bool
  sample:
    [
      {
        "name"     : "Timezone",
        "old_value": "UTC (UTC, +0000)",
        "new_value": "Asia/Tokyo (JST, +0900)",
        "command"  : "timedatectl set-timezone Asia/Tokyo",
        "changed"  : True
      },
      {
        "name"     : "NTP enabled",
        "old_value": "yes",
        "new_value": "yes",
        "command"  : "",
        "changed"  : False
      }
    ]
'''

EXAMPLES = '''
- name: set timezone to Asia/Tokyo
  timedatectl: timezone=Asia/Tokyo
'''


def main():
    # Arguments setting
    # * 'name' is not required key to construct AnsibleModule,
    #   but it is used to check if change will happen.
    arguments = dict(
        ntp      = dict(default=None, required=False, type='bool', name='NTP enabled'),
        time     = dict(default=None, required=False, type='str',  name='Local time'),
        timezone = dict(default=None, required=False, type='str',  name='Timezone'),
    )
    changes = []

    # Construct 'module'
    module = AnsibleModule(
        argument_spec       = arguments,
        supports_check_mode = True,
        required_one_of     = [ arguments.keys() ],
    )

    # Get the current state from the stdout of status the command
    old_state = module.run_command('timedatectl status', check_rc=True)[1]
    # module.exit_json(changed=False, msg=old_state) # For debug

    changed_any = False
    for arg, spec in arguments.iteritems():
        if module.params[arg] is not None:
            if spec['type'] != 'bool':
                new_value = module.params[arg]
            else:
                # new_value = 'yes' if module.params[arg] else 'no'
                if module.params[arg]:
                    new_value = 'yes'
                else:
                    new_value = 'no'
            # Check the old value, which is written in `old_state`.
            # Below regex is to find the value.
            regex = re.compile(spec['name']+r':\s*([^\n]+)\n')
            old_value = regex.search(old_state).group(1)
            if new_value not in old_value:
                # then, changes should happen!
                command = 'timedatectl set-%s %s' % (arg, new_value)
                changed = True
                changed_any = True
            else:
                command = ''
                changed = False
            changes.append(
                dict(
                    name      = spec['name'],
                    new_value = new_value,
                    old_value = old_value,
                    command   = command,
                    changed   = changed
                )
            )

    # Make changes
    if not module.check_mode:
        for change in changes:
            if change['changed']:
                module.run_command(change['command'], check_rc=True)
        # Update 'new_value' field
        new_state = module.run_command('timedatectl status', check_rc=True)[1]
        for change in changes:
            regex = re.compile(change['name']+r':\s*([^\n]+)\n')
            change['new_value'] = regex.search(new_state).group(1)

    module.exit_json(changed=changed_any, changelogs=changes)


from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
