import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { expect, test } from "vitest";

const css = readFileSync(resolve(process.cwd(), "src/styles.css"), "utf8");

test("desktopはselector・主表示・inspectorの三領域を持つ", () => {
  expect(css).toMatch(/\.viewer-shell\s*\{[^}]*grid-template-columns:/s);
  expect(css).toMatch(/minmax\(0,\s*1fr\)/);
});

test("mobileはselectorをviewport下端のsheetへ移す", () => {
  const mobile = css.slice(css.indexOf("@media (max-width: 760px)"));

  expect(mobile).toMatch(/\.selector-rail\s*\{[^}]*position:\s*fixed;/s);
  expect(mobile).toMatch(/\.selector-rail\s*\{[^}]*bottom:\s*0;/s);
  expect(mobile).toMatch(/\.selector-rail\s*\{[^}]*visibility:\s*hidden;/s);
  expect(mobile).toMatch(/\.selector-rail\.open\s*\{[^}]*visibility:\s*visible;/s);
  expect(mobile).toMatch(/\.mobile-item-bar\s*\{[^}]*display:\s*grid;/s);
});
