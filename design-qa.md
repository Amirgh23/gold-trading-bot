# Pulse Matrix Design QA

- Source visual truth: `artifacts/pulse-matrix-reference.png` (local QA artifact)
- Implementation capture: `artifacts/pulse-matrix-final.png`
- Combined comparison: `artifacts/pulse-matrix-comparison.png`
- Source pixels: 1487 × 1058
- Implementation pixels: 1496 × 979 (1480 × 940 Qt logical window plus native frame)
- State: market workspace, paper environment, demo feed running

## Full-view comparison

The implementation preserves the selected direction's obsidian base, electric
cyan interaction color, violet structural accent, gold instrument emphasis,
compact terminal typography, dominant market chart, decision log, and protected
risk/action column. Density was intentionally reduced from the concept so the
desktop application remains readable at 1180 × 760 and does not imply live order
book or margin data that the product does not possess.

## Focused comparison

- Typography: Segoe UI and Cascadia Mono provide the same sans/monospace split;
  hierarchy, wrapping, and label contrast are readable in the captured window.
- Spacing: 12–18 px section rhythm and thin separators match the reference. The
  final pass removed a duplicate brand block and added useful guardrail rows.
- Colors: tokenized violet/cyan/obsidian palette matches the visual direction;
  gold is limited to PAXG price and red/green are reserved for state changes.
- Assets: the target contains no required photographic or illustrative assets;
  the chart is native Qt rendering and stays sharp at desktop scale.
- Copy: fake AI and guaranteed-return language were removed. Demo feed, paper
  mode, circuit breaker, and configured guardrails are explicit.

## Interaction evidence

- Sidebar navigation switched successfully between Market and Backtest.
- Halt Demo Feed changed feed status to halted and exposed Resume Demo Feed.
- Timeframe controls render complete labels and exclusive selected styling.
- Paper ticket remains explicitly non-live and protected by an explanatory dialog.

## Comparison history

1. P2: nested violet borders appeared around every label in the signal panel.
   Fixed by scoping styles to named frames; the next desktop capture showed clean
   label surfaces.
2. P2: `15m` was clipped at the initial button width. Fixed by increasing the
   control width and verifying the accessible label is complete.
3. P2: duplicated Pulse Matrix branding weakened hierarchy and the right rail had
   unused space. Fixed by keeping branding in the sidebar and adding risk
   guardrails to the rail.

No actionable P0, P1, or P2 findings remain. The simplified information density
is an intentional product constraint rather than fidelity drift.

final result: passed
