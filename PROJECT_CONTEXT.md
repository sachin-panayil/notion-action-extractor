# Project Context: Why I Built This

## The Problem I Had

I use a Notion kanban board to track my projects, and I got into the habit of writing quick updates directly in the Notes field of each card. This was great because I could see what was happening with each project right from the board view without having to click into every single ticket.

My typical workflow looked like this - I'd update cards with notes like:

```
11/4
- Created a PR
- Waiting on approval from owner

11/18
- Fixed linting
- Still waiting on approval

12/17
- Reached out to a maintainer but no response
ACTION: Reach out to another maintainer
ACTION: Schedule follow-up meeting with team
```

This worked well when I had a few projects, but as I took on more work, the visual clutter became overwhelming. I'd have dozens of kanban cards, each with their own ACTION items scattered throughout the notes, and it became nearly impossible to get a clear picture of what I actually needed to do.

## What I Really Wanted

I wanted to keep my natural note-taking workflow (writing updates and ACTION items directly in the kanban notes) but have a way to automatically extract all those ACTION items into a clean, sortable, filterable list that I could actually manage.

Basically, I wanted the best of both worlds:
- Keep my project context and updates visible on the kanban board
- Have a separate "master to-do list" of all ACTION items that I could prioritize and track

## How the Solution Works

The system I built does exactly what I was hoping for:

1. **Monitors my kanban board** for any cards that contain "ACTION:" in their notes
2. **Extracts each ACTION item** and creates a separate entry in a Master Action Items database
3. **Links everything back** so I can see which project each action came from
4. **Syncs completion status** - when I check off an item in my master list, it adds a ✅ to the original kanban note
5. **Runs automatically** throughout the day so I don't have to think about it

Now I can continue my same note-taking habits, but I get a clean, organized view of all my action items that I can sort by priority, filter by project, and actually manage effectively.

## Setting Up the Notion Databases

To make this work, you need two databases set up properly:

### Your Kanban Board (probably already exists)
You'll need to add a couple of properties if you don't have them:
- **Notes** (Rich Text) - where you write your updates and ACTION items
- **Last Processed** (Date) - the system uses this to track what it's already processed
- **Priority** (Select) - optional but useful for sorting action items later

### Master Action Items Database (new)
This is where all your extracted ACTION items will live:
- **Action Item** (Title) - the actual task text
- **Status** (Checkbox) - for marking things complete  
- **Source Card** (Relation) - links back to your kanban card
- **Priority** (Rollup) - pulls priority from your kanban card so you can sort
- **Date Added** (Created Time) - when the action was extracted

The relation between these databases is key - it's what lets you see which project each action item came from and enables the completion sync back to your original notes.

## Running It Automatically

I set this up to run via GitHub Actions three times a day (morning, afternoon, evening) so it stays current without me having to remember to trigger it manually. All the sensitive stuff like API tokens are stored as GitHub secrets for security.

## Why I'm Sharing This

This is definitely a pretty specific use case that matches my particular workflow, but I figured there might be other people out there who find themselves in a similar situation - wanting to keep their natural note-taking style while also having better organization and tracking of their action items.

The solution handles a lot of edge cases I ran into (like timezone issues, duplicate prevention, handling multiple ACTION items in the same note) so hopefully it can save someone else the trouble of figuring all that out from scratch.

Even if your exact workflow is different, the core concept of automatically extracting structured data from free-form notes and maintaining bidirectional sync might be useful for other automation projects.
