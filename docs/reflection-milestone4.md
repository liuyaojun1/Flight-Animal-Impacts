# Milestone 4 Reflection

**Implemented Features and Feedback Integration**

Our FAA Aircraft Wildlife Strikes dashboard has evolved into a highly interactive, production-ready application, heavily guided by peer and TA feedback. User testing indicated that the application was intuitive, but a recurring theme in our Milestone 3 feedback was the need for immediate geographic context. 

The most valuable insight we received was the suggestion to incorporate an interactive map. In response, we dedicated significant effort to implementing a US Choropleth map linked directly to a "Top 10 States" bar plot. Hovering over a state in the bar chart highlights it on the map, and clicking a state cross-filters the entire dashboard. Handling the heavily right-skewed speed and height data also required a mathematical approach; we implemented a `log1p` transformation and built a dynamic histogram to accurately display these distributions. To further polish the user experience, we engineered a click-and-drag date range selector on the Yearly Trend plot, a collapsible interaction guide, and a functional "Reset Filters & Charts" button. 

**Feature Prioritization and Design Choices**

To deliver a stable, professional application, we had to make strict design choices regarding our planned features. We originally intended to include additional granular dropdown filters, such as "Time of Day" and "Bird Size." However, integrating the new map and log-scale visualizations took priority. We explicitly chose to drop the extra filters to prevent UI clutter and maintain a strict, responsive, single-page layout without scrolling. Ensuring the core visualizations rendered beautifully on one screen was a higher priority for usability than adding secondary filters.

**Known Edge Cases and Future Enhancements**

While the core application is fully functional and performant, there are a few edge cases we have documented for future development:
* **Native Vega Menu Limitations:** Altair generates a default action menu ("...") on charts. While saving images works, clicking "View Source" or "Open in Vega Editor" currently disrupts the dashboard environment. This is a known library limitation we plan to disable or override in future patches.
* **Redundant UI Elements:** We are aware of minor text redundancies in the current build, such as displaying both "Total Records" and "Incidents," and repeating the 2015 partial data disclaimer.
* **Future Optimization:** Cross-filtering the large dataset across all six plots simultaneously handles a massive amount of data; future versions would focus on backend caching to improve sluggish callback speeds during heavy interaction.
