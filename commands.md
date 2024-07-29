# Chief Productivity Officer (CPO) Discord Bot Commands

This document provides a detailed explanation of all commands available in the Chief Productivity Officer Discord bot.

## Pomodoro Commands

### Individual Pomodoro

1. **Start a Pomodoro Session**
   - Command: `/start` or `!start`
   - Description: Starts an individual Pomodoro session.
   - Usage: User must be in a voice channel to use this command.
   - Example: `!start`

2. **Set Pomodoro Timings**
   - Command: `/set_pomodoro_timings <work> <short_break> <long_break>` or `!set_pomodoro_timings <work> <short_break> <long_break>`
   - Description: Sets custom Pomodoro timings for work, short break, and long break periods.
   - Parameters:
     - `<work>`: Duration of work period in minutes
     - `<short_break>`: Duration of short break in minutes
     - `<long_break>`: Duration of long break in minutes
   - Example: `!set_pomodoro_timings 25 5 15`

### Group Pomodoro

1. **Create a Pomodoro Group**
   - Command: `/group create <group_name>` or `!group create <group_name>`
   - Description: Creates a new Pomodoro group.
   - Parameters:
     - `<group_name>`: Name of the group to create
   - Example: `!group create study_buddies`

2. **Add Member to Pomodoro Group**
   - Command: `/group add <group_name> @member` or `!group add <group_name> @member`
   - Description: Adds a member to an existing Pomodoro group.
   - Parameters:
     - `<group_name>`: Name of the existing group
     - `@member`: Mention of the user to add
   - Example: `!group add study_buddies @JohnDoe`

3. **Remove Member from Pomodoro Group**
   - Command: `/group remove <group_name> @member` or `!group remove <group_name> @member`
   - Description: Removes a member from a Pomodoro group.
   - Parameters:
     - `<group_name>`: Name of the existing group
     - `@member`: Mention of the user to remove
   - Example: `!group remove study_buddies @JohnDoe`

4. **Start Group Pomodoro Session**
   - Command: `/group start <group_name>` or `!group start <group_name>`
   - Description: Starts a Pomodoro session for the entire group.
   - Parameters:
     - `<group_name>`: Name of the group to start the session for
   - Usage: The user must be in a voice channel to use this command.
   - Example: `!group start study_buddies`

## Check-in Commands

1. **Set Check-in Channels**
   - Command: `/checkin_channels #channel1 #channel2 ...` or `!checkin_channels #channel1 #channel2 ...`
   - Description: Sets channels where check-in sessions can be started.
   - Parameters:
     - `#channel1 #channel2 ...`: One or more channel mentions
   - Permissions: Requires manager or admin permissions.
   - Example: `!checkin_channels #productivity #study-group`

2. **Start a Check-in Session**
   - Command: `/checkin <duration> @mention` or `!checkin <duration> @mention`
   - Description: Starts a check-in session with specified duration and mention.
   - Parameters:
     - `<duration>`: Duration of the check-in session (format: number + s/m/h/d)
     - `@mention`: User or role to mention for the session
   - Example: `!checkin 30m @StudyGroup`

3. **Add Bot Managers**
   - Command: `/managers_add @user_or_role` or `!managers_add @user_or_role`
   - Description: Adds users or roles to the list of bot managers.
   - Parameters:
     - `@user_or_role`: Mention of the user or role to add as manager
   - Permissions: Requires admin permissions.
   - Example: `!managers_add @Moderators`

4. **View Bot Managers**
   - Command: `/managers_view` or `!managers_view`
   - Description: Displays the current list of bot managers.
   - Permissions: Requires admin permissions.
   - Example: `!managers_view`

## Duration Format

For commands that require a duration (like `checkin`), use the following format:
- `<number><unit>`, where unit can be:
  - `s` for seconds
  - `m` for minutes
  - `h` for hours
  - `d` for days

Examples:
- `30m` for 30 minutes
- `1h` for 1 hour
- `2d` for 2 days

## Interaction with Check-in Sessions

During an active check-in session, users can interact using the following buttons:
- **Join**: Allows a user to join the current check-in session.
- **Leave**: Allows a user to leave the current check-in session (not available for the session creator).
- **End**: Ends the current check-in session (only available for the session creator).

## Notes

- The bot uses both `/` and `!` as command prefixes. You can use either.
- Some commands require specific permissions (manager or admin) to use.
- Pomodoro sessions will automatically cycle through work and break periods until manually stopped or all participants leave the voice channel.
- Check-in sessions will send periodic reminders to participants until the session ends.
This COMMANDS.md file provides a comprehensive explanation of all the commands available in the Chief Productivity Officer Discord bot, including their usage, parameters, and examples. It also includes information about duration formats and interaction with check-in sessions.