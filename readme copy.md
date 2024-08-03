
# Chief Productivity Officer (CPO) Discord Bot

Chief Productivity Officer (CPO) is a Discord bot designed to enhance productivity and organization within your Discord server. It offers Pomodoro sessions, check-in reminders, and customizable settings to help users stay focused and collaborate efficiently.

## Features

- **Pomodoro Sessions**: Start individual or group Pomodoro sessions with configurable work, short break, and long break durations.
- **Check-In Sessions**: Schedule check-in sessions for task updates and collaboration, with random reminders.
- **Dynamic Voice Channels**: Automatically manage voice channels for Pomodoro sessions.
- **User Statistics**: Track user Pomodoro sessions and check-ins using an SQLite database.
- **Customizable Permissions**: Control bot settings and commands through role-based permissions.

## Installation

1. Clone the repository:
    \`\`\`bash
    git clone https://github.com/Vectorphy/CPO.git
    cd CPO
    \`\`\`

2. Install the required dependencies:
    \`\`\`bash
    pip install -r requirements.txt
    \`\`\`

3. Set up your Discord bot:
    - Create a new application on the [Discord Developer Portal](https://discord.com/developers/applications).
    - Add a bot to your application and copy the bot token.
    - Invite the bot to your server with the necessary permissions.

4. Create a \`.env\` file in the project root and add your bot token:
    \`\`\`
    DISCORD_BOT_TOKEN=your_bot_token_here
    \`\`\`

5. Run the bot:
    \`\`\`bash
    python bot.py
    \`\`\`

## Usage

For a full list of available commands and their usage, please refer to the [COMMANDS.md](COMMANDS.md) file.

## Project Structure

- \`bot.py\`: Main bot file that initializes and runs the bot.
- \`database.py\`: Handles all database operations.
- \`utils.py\`: Contains utility functions used across the bot.
- \`cogs/\`:
  - \`__init__.py\`: Initializes the cogs package.
  - \`pomodoro.py\`: Implements Pomodoro session functionality.
  - \`checkin.py\`: Implements check-in session functionality.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (\`git checkout -b feature/AmazingFeature\`)
3. Commit your changes (\`git commit -m 'Add some AmazingFeature'\`)
4. Push to the branch (\`git push origin feature/AmazingFeature\`)
5. Open a Pull Request


## Acknowledgments

- Discord.py library
- SQLite database
- All contributors and users of this bot

## Support

If you encounter any problems or have any questions, please open an issue on this repository.
