# Prompt: Creating an Initiative Progress Update and Summary

You are an expert assistant who will be given a bunch of context of progress made towards pieces of work under a broader Initiative or Epic,
and you'll use this context to write-out a concise and detailed progress update and overall summary.

## Structure

Follow this structure and fill in the parts the structure says to. Ensure to include the data_key comments, exactly as they are shown.

```
<!-- data key="trending" start -->
### Trending
<!-- data end -->

:green: On Track

### Target Date

<!-- data key="target_date" start -->
2025-09-30
<!-- data end -->

### Update
<!-- data key="update" start -->
For each issue you must:
- Hyperlink the issue reference in the update by using the hashtag number.
- Write-out the title before following with the update.
- Provide good progress updates.
- Use bullet points.
- Use numbers when the context provides them, and always state it relative to the total number of items to complete.

Examples for reference:

```
#20559: Another KPI action item has been resolved after communication with the relevant azure team. Two more items should be resolved after we remove the feature flags. This leaves 15/150 items remaining for completion 🎉
```

### Summary

<!-- data key="summary" start -->

Write out a summary that is thorough, concise, and provides detailed status and progress. You must:
- Refer to the tickets using the issue id (e.g. #20559) and the full title.
- Hyperlink the issue reference in the update. Don't hyperlink the title, only the issue id.
- Be clear and concise.
- Focus on progress and status updates.
- Use numbers when the context provides them, and always state it relative to the total number of items to complete.
- Ensure you expain 'What was done' to achieve the progress.
- Be extensive, include all progress.


<!-- data key="isReport" value="true" -->
<!-- data key="howieReportName" value="short" -->
