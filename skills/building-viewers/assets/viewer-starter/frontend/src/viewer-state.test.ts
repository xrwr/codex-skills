import { parseViewerState, serializeViewerState } from "./viewer-state";
import { expect, test } from "vitest";

test("共有するitem選択をquery parameterから復元する", () => {
  expect(parseViewerState("?item=item%2F1")).toEqual({ itemId: "item/1" });
});

test("item選択だけをquery parameterへ保存する", () => {
  expect(serializeViewerState({ itemId: "item 1" })).toBe("?item=item+1");
});
