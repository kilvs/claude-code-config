# Edit safety

- Utility and global classes are shared — editing one changes every element that uses it. Check usage before touching a utility class. If the change is for one instance, use a Component variant (on a Component) or an `is-*` combo (on a non-component class) instead.
- Never rename classes inside an existing component definition; it affects every instance. Legacy classes inside older components are tolerated — do not refactor them opportunistically.
- Before running **Clean Up unused styles**, confirm every runtime-only `is-*` class has its sample in the Style Guide page's **State classes** section; a Designer class with no instance is deleted.
- Never publish the site. Stage changes, then summarize exactly what changed so the site owner can review and publish.
- Before finishing any task, verify: no auto-generated class names remain, no hardcoded values where a token exists, structure follows the core-structure rule, and every custom class shares its block's identifier prefix.
- Check the work on **every breakpoint** — base desktop and tablet / mobile landscape / mobile portrait, plus any larger breakpoint the site has — for overflow, unintended wrapping, and spacing breakage. Also view the base breakpoint at 992, 1440 and 3440 wide (the nav must fit at 992; ultrawide must stay contained with full-bleed grounds). Never sign off from the base breakpoint alone.
