# Campaign Templates

Campaign templates allow you to predefine your campaign world before starting play. Instead of building everything dynamically during gameplay, you can set up NPCs, locations, plot threads, and the overarching goal in advance.

## Using Templates

### Creating a Campaign from a Template
1. Create or copy a campaign template JSON file to `data/campaign_templates/`
2. When starting a new campaign in the game, select "Load from Template"
3. Choose your template file
4. The campaign will be initialized with all predefined content

### Template Structure

See `template_blank.json` for the complete structure. Key sections:

- **name**: Campaign title
- **setting**: World description and atmosphere
- **overarching_goal**: Main quest objective
- **npcs**: Predefined NPCs with knowledge, relationships, and roles
- **locations**: Places in your world with events and NPCs present
- **plot_threads**: Story arcs with status tracking
- **metadata**: Tags and information about the campaign

### Example Templates

- **lost_crown_of_eldoria.json**: A medieval fantasy campaign involving political intrigue and a stolen crown
- **template_blank.json**: Empty template for creating your own

## Benefits of Templates

✅ **Consistency**: NPCs and locations are defined upfront with their knowledge and relationships  
✅ **Preparation**: Plan your campaign structure before the first session  
✅ **Reusability**: Share campaign templates with others or reuse your favorites  
✅ **DM Context**: The AI DM automatically knows about all predefined elements  

## Creating Your Own Template

1. Copy `template_blank.json` to a new file
2. Fill in your campaign details
3. Define NPCs with their knowledge and relationships
4. Set up locations and notable events
5. Create initial plot threads (usually 2-4 active threads)
6. Add metadata for organization

## Tips

- **NPCs**: Include what they know, who they're connected to, and their role
- **Locations**: Note which NPCs are present and what has happened there
- **Plot Threads**: Start with "active" status; the DM will track updates during play
- **Relationships**: Define key relationships between NPCs for realistic interactions
- **Knowledge**: What each NPC knows drives how they interact with players

## Template vs. Dynamic

You can mix both approaches:
- Use templates to define the starting world
- Let the DM create new NPCs, locations, and plots dynamically during play
- All additions are automatically tracked in the campaign file

Templates give structure; dynamic play adds spontaneity.
