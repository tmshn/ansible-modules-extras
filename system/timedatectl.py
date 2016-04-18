#!/usr/bin/python
# -*- coding: utf-8 -*-

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

EXAMPLES='''
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

    # Construct 'module'
    module = AnsibleModule(
        argument_spec       = arguments,
        supports_check_mode = True,
        required_one_of     = [ arguments.keys() ],
    )

    # Get the current state from the stdout of status the command
    old_state = module.run_command('timedatectl status', check_rc=True)[1]
    # module.exit_json(changed=False, msg=old_state) # For debug

    for arg,spec in arguments.items(): # use `items` instead of `iteritems` to delete safely
        if module.params[arg] is None:
            del arguments[arg]
        else:
            if spec['type']!='bool':
                spec['new_value'] = module.params[arg]
            else:
                spec['new_value'] = 'yes' if module.params[arg] else 'no'
            # Check the old value, which is written in `old_state`.
            # Below regex is to find the value.
            regex = re.compile(spec['name']+r':\s*([^\n]+)\n')
            spec['old_value'] = regex.search(old_state).group(1)
            if spec['new_value'] not in spec['old_value']:
                # then, changes should happen!
                spec['command'] = 'timedatectl set-%s %s' % (arg, spec['new_value'])

    # Make changes
    if not module.check_mode:
        for arg,spec in arguments.iteritems():
            if 'command' in spec:
                module.run_command(spec['command'], check_rc=True)
        # Get the new state to compare the changes
        new_state = module.run_command('timedatectl status', check_rc=True)[1]
        for arg,spec in arguments.iteritems():
            regex = re.compile(spec['name']+r':\s*([^\n]+)\n')
            spec['new_value'] = regex.search(new_state).group(1)


    # Construct the message
    message = '# Changes\n'
    changed = False
    for arg,spec in arguments.iteritems():
        message += '  - '
        if 'command' in spec:
            changed = True
            message += 'o'
        else:
            message += 'x'
        message += ': ['+spec['name']+']\t'+spec['old_value']+' -> '+spec['new_value']+'\n'
    message += '(x: not changed / o: changed)\n'

    module.exit_json(changed=changed, msg=message)


from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
