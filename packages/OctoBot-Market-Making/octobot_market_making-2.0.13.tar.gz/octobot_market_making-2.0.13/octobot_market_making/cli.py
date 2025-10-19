#  This file is part of OctoBot Market Making (https://github.com/Drakkar-Software/OctoBot-Market-Making)
#  Copyright (c) 2025 Drakkar-Software, All rights reserved.
#
#  OctoBot is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  OctoBot is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public
#  License along with OctoBot. If not, see <https://www.gnu.org/licenses/>.
import sys
import octobot.cli

import octobot_market_making.constants


def main():
    # Start OctoBot with a default config file configured to use
    # the market making distribution and profile
    octobot.cli.main(
        sys.argv[1:],
        default_config_file=octobot_market_making.constants.DEFAULT_CONFIG_FILE
    )