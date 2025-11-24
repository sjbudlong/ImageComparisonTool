# Markdown Export Feature

## Overview

The Image Comparison Tool now exports summary reports in **Markdown format** specifically designed for CI/CD pipeline integration, particularly **Azure DevOps**. This enables seamless embedding of comparison results into build pipelines and automated notifications.

## Architecture

### New Module: `markdown_exporter.py`

A dedicated module handling all markdown export functionality:

```python
from markdown_exporter import MarkdownExporter

exporter = MarkdownExporter(output_dir)
exporter.export_summary(results)  # Returns: Path to summary.md
```

**Design Rationale for Separate File:**
- **Separation of Concerns**: HTML generation stays in `report_generator.py`, markdown in `markdown_exporter.py`
- **Testability**: Markdown logic can be tested independently
- **Maintainability**: Easy to extend with additional export formats (JSON Schema, XML, etc.)
- **Reusability**: Can be imported and used independently of report generation

## Features

### Generated Report: `summary.md`

The markdown exporter generates a comprehensive summary with:

1. **Overview Statistics**
   - Total comparisons
   - Count by status: Nearly Identical, Minor, Moderate, Major

2. **Difference Metrics Table**
   - Maximum, minimum, and average differences
   - Easy to parse for pipeline thresholds

3. **Overall Status Assessment**
   - Single-line determination for automated decision-making
   - Emoji indicators for visual scanning (✅ ⚠️ ❌)

4. **Detailed Results Table**
   - Per-file comparison status
   - Color-coded indicators (emoji)
   - Markdown-formatted filename for copy-paste

5. **Azure DevOps Integration**
   - Embedded pipeline configuration example
   - Instructions for attaching to build artifacts

## Azure DevOps Integration

### Step 1: Capture Markdown in Pipeline

```yaml
steps:
  - task: PythonScript@0
    inputs:
      scriptSource: 'filePath'
      scriptPath: 'main.py'
      arguments: '--base-dir $(Build.ArtifactStagingDirectory) --new-dir images/new --known-good-dir images/baseline'

  - task: PublishBuildArtifacts@1
    inputs:
      PathtoPublish: '$(Build.ArtifactStagingDirectory)/reports'
      ArtifactName: 'image-comparison-reports'
```

### Step 2: Parse Markdown for Decisions

```yaml
  - pwsh: |
      $content = Get-Content '$(Build.ArtifactStagingDirectory)/reports/summary.md'
      if ($content -match 'Major Differences') {
          Write-Host "##vso[task.logissue type=warning] Image differences detected"
      }
```

### Step 3: Embed in Build Summary

```yaml
  - task: UploadBuildLog@1
    inputs:
      LogFolderPath: '$(Build.ArtifactStagingDirectory)/reports'
```

## Output Format

### Example Markdown Output

```markdown
# Image Comparison Summary

## Statistics

- **Total Comparisons**: 15
- **Nearly Identical** (<0.1%): 12
- **Minor Differences** (0.1-1%): 2
- **Moderate Differences** (1-5%): 1
- **Major Differences** (≥5%): 0

## Difference Statistics

| Metric | Value |
|--------|-------|
| Maximum Difference | 3.4521% |
| Minimum Difference | 0.0031% |
| Average Difference | 0.5234% |

## Overall Status

✅ **All comparisons passed**

## Detailed Results

| # | Filename | Difference % | Status |
|---|----------|-------------|--------|
| 1 | `render_001.png` | 0.0031% | ✅ Nearly Identical |
| 2 | `render_002.png` | 0.5234% | ⚠️ Minor Differences |
| ...| ...      | ...         | ...    |

---

## Reports

- [HTML Summary Report](summary.html) - Interactive dashboard with images
- [Results JSON](results.json) - Machine-readable format
```

## API Usage

### Basic Usage

```python
from markdown_exporter import MarkdownExporter
from pathlib import Path

# Create exporter instance
exporter = MarkdownExporter(Path('reports'))

# Export comparison results
results_path = exporter.export_summary(comparison_results)
print(f"Markdown report saved to: {results_path}")
```

### In Comparator Pipeline

The markdown export is automatically called:

```python
# In comparator.py _generate_reports()
markdown_exporter = MarkdownExporter(self.config.html_path)
markdown_exporter.export_summary(results)
```

## Status Determination

The exporter automatically determines overall status:

- ✅ **All comparisons passed** - No major differences
- ⚠️ **Minor issues detected** - ≤10% of images have major differences
- ❌ **Significant issues detected** - >10% of images have major differences

This enables simple pass/fail decision-making in CI/CD:

```bash
# Check for failures
grep -q "Significant issues" summary.md && exit 1
```

## Integration Patterns

### GitHub Actions

```yaml
- name: Generate comparison reports
  run: python main.py --base-dir ${{ runner.workspace }}

- name: Upload reports
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: image-comparisons
    path: reports/

- name: Comment on PR
  if: github.event_name == 'pull_request'
  uses: actions/github-script@v6
  with:
    script: |
      const fs = require('fs');
      const md = fs.readFileSync('reports/summary.md', 'utf8');
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: md
      });
```

### GitLab CI

```yaml
image_comparison:
  script:
    - python main.py --base-dir $CI_PROJECT_DIR
  artifacts:
    reports:
      dotenv: reports/summary.md
    paths:
      - reports/
```

## Benefits

✅ **Pipeline-Agnostic**: Works with Azure DevOps, GitHub Actions, GitLab CI, Jenkins, etc.
✅ **Human-Readable**: Markdown renders well in web interfaces and email
✅ **Machine-Parseable**: Easy regex patterns for automated decisions
✅ **Low Overhead**: Lightweight markdown generation
✅ **Consistent Format**: Standardized structure across runs
✅ **Emoji Support**: Visual indicators work in all platforms

## File Outputs

After comparison, three formats are available:

| File | Format | Use Case |
|------|--------|----------|
| `summary.html` | Interactive HTML | View in browser, detailed analysis |
| `summary.md` | Markdown | CI/CD pipelines, email notifications, documentation |
| `results.json` | JSON | Programmatic processing, data analysis |

All three can coexist and serve different purposes in your workflow.
