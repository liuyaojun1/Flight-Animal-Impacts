**Our FAA Aircraft Wildlife Strikes dashboard has improved a lot since the last milestone in many ways:**

- We added a plot to show strike counts by state on an interactive map of the USA. Clicking a state filters other plots to only data for that state, and hovering over a state reveals the strike information for that state. This helps the user locate areas where aircraft-wildlife impacts needs to be addressed most. The map plot is linked to the bar plot below it. Hovering over any state in the bar plot highlights the same state in the map plot. This added interactivity was added based on the feedback from Milestone 3.
- We also added a histogram that can display the distribution of strikes over either speed or height. Users can select which is displayed using a dropdown. Hovering over a bar gives the count number for that bar.
- We added a collapsable information guide to help users interact with the dashboard.
- A date range can now be selected on the Yearly Trend plot by simply clicking and dragging your mouse, which filters the data in the other plots. 
- We also added more colour to the bar plots to increase visual appeal. 
- We added a button with a label of "..." that gives options to save specific states of the dashboard in different formats. This was suggested by our Milestone 3 feedback.
- We added a Reset Filters and Charts button to help users return the dashboard to its default state.

**Dropped Features:**

- We originally planned to include additional granular filters (such as "Time of Day" or "Bird Size"). However, we ultimately chose not to include them to prevent UI clutter. Maintaining a strict single-page, no-scroll layout was a higher priority for usability than adding more dropdowns.
- We used to display "Total Records" and "Incidents" in the KPI cards, which is redundant since every record is an incident.

**The dashboard is still a work in progress. These are planned features yet to be completed:**

- Remove duplicate information. We mention that the data for 2015 does not cover the entire year in 2 places. One will be removed to avoid repetition.
- More intuitive colours. Fatalities will be show in red, Injuries in orange, With Damage in yellow, and Incidents in blue. This way the colours will intuitively indicate the severity.
- The speed/height histogram would be more useful as a log-log plot than a semi-log plot since most impacts occur at 0 height and relatively low speeds.
- The "..." button gives options to View Source, View Compiled Vega, and Open in Vega Editor. These options are in progress. Currently, clicking them crashes the dashboard.
- We will try to improve loading speed.