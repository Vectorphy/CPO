
# Chief Productivity Officer (CPO) Discord Bot Commands

This document provides a detailed explanation of all commands available in the Chief Productivity Officer Discord bot.

## Study Groups

1. **Create a Study Group**
   - Command: `/create_group <name> [max_size]`
   - Description: Creates a new study group with an optional maximum size.
   - Usage: Assigns a role to the group and creates a voice channel.
   - Example: `/create_group study_buddies 5`

2. **Join an Existing Study Group**
   - Command: `/join_group`
   - Description: Joins the user to an existing study group.
   - Usage: Assigns the group role to the user and moves them to the voice channel if it exists.
   - Example: `/join_group`

3. **Leave the Current Study Group**
   - Command: `/leave_group`
   - Description: Leaves the user from the current study group.
   - Usage: Removes the group role from the user.
   - Example: `/leave_group`

4. **End the Current Study Group (Creator Only)**
   - Command: `/end_group`
   - Description: Ends the current study group.
   - Usage: Deletes the group role and voice channel.
   - Example: `/end_group`

## Pomodoro

1. **Start a Pomodoro Session**
   - Command: `/start_pomodoro [focus] [short_break] [long_break]`
   - Description: Starts a Pomodoro session with optional timings.
   - Usage: Creates a voice channel if it doesn't exist and moves the user.
   - Example: `/start_pomodoro 25 5 15`

2. **End the Current Pomodoro Session**
   - Command: `/end_pomodoro`
   - Description: Ends the current Pomodoro session.
   - Example: `/end_pomodoro`

3. **Pause the Current Pomodoro Session**
   - Command: `/pause_pomodoro`
   - Description: Pauses the current Pomodoro session.
   - Example: `/pause_pomodoro`

4. **Resume the Paused Pomodoro Session**
   - Command: `/resume_pomodoro`
   - Description: Resumes the paused Pomodoro session.
   - Example: `/resume_pomodoro`

## Management

1. **Add a Bot Developer**
   - Command: `/add_bot_developer <user>`
   - Description: Adds a user as a bot developer (Bot Developer only).
   - Example: `/add_bot_developer @User`

2. **Add a Guild Manager**
   - Command: `/add_guild_manager <user>`
   - Description: Adds a user as a guild manager (Bot Developer only).
   - Example: `/add_guild_manager @User`

3. **Remove a Guild Manager**
   - Command: `/remove_guild_manager <user>`
   - Description: Removes a user from the guild managers (Bot Developer only).
   - Example: `/remove_guild_manager @User`

4. **List All Managers**
   - Command: `/list_managers`
   - Description: Lists all managers for the server.
   - Example: `/list_managers`

## Notes

- Users can only be in one study group at a time.
- Joining a group automatically assigns a role and moves the user to the group's voice channel.
- Pomodoro notifications are sent to the group's voice channel or a text channel if the voice channel is not available.
- Only group creators can end groups, and only bot developers can manage bot permissions.
