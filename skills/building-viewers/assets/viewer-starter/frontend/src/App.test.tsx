import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { App } from "./App";


const ITEMS = [
  { id: "item-1", name: "Sample one", kind: "series", status: "ready", metadata: { split: "train" } },
  { id: "item-2", name: "Sample two", kind: "series", status: "partial", metadata: { split: "test" } },
];

function jsonResponse(body: unknown, ok = true): Response {
  return { ok, status: ok ? 200 : 503, json: async () => body } as Response;
}

describe("Viewer shell", () => {
  beforeEach(() => {
    window.history.replaceState({}, "", "/data?item=item-1");
    vi.stubGlobal("fetch", vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url === "/api/items") return Promise.resolve(jsonResponse(ITEMS));
      if (url === "/api/issues") return Promise.resolve(jsonResponse([]));
      if (url.includes("item-1")) {
        return Promise.resolve(jsonResponse({ ...ITEMS[0], description: "First detail", metrics: { score: 0.91 }, preview: { type: "values", values: [1, 2, 3] } }));
      }
      return Promise.resolve(jsonResponse({ ...ITEMS[1], description: "Second detail", metrics: { score: 0.42 }, preview: { type: "values", values: [3, 2, 1] } }));
    }));
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    window.localStorage.clear();
  });

  it("URL選択を復元し、一覧・主表示・詳細を同じitemへ同期する", async () => {
    render(<App />);

    expect(screen.getByText("Loading catalog…")).toBeInTheDocument();
    expect(await screen.findByRole("heading", { name: "Sample one" })).toBeInTheDocument();
    expect(screen.getByText("First detail")).toBeInTheDocument();
    expect(screen.getByText("1, 2, 3")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /Sample two/ }));

    expect(await screen.findByRole("heading", { name: "Sample two" })).toBeInTheDocument();
    await waitFor(() => expect(window.location.search).toBe("?item=item-2"));
  });

  it("desktop sidebarを端末固有状態として保存する", async () => {
    render(<App />);
    await screen.findByRole("heading", { name: "Sample one" });

    await userEvent.click(screen.getByRole("button", { name: "Collapse sidebar" }));

    expect(window.localStorage.getItem("__VIEWER_PACKAGE_DASHED__.sidebar-collapsed")).toBe("true");
  });

  it("mobile selectorへfocusを移し、Escapeで起点へ戻す", async () => {
    render(<App />);
    await screen.findByRole("heading", { name: "Sample one" });
    const chooser = screen.getByRole("button", { name: /Sample one.*Choose item/ });

    await userEvent.click(chooser);
    const selector = screen.getByRole("complementary", { name: "Item selector" });
    expect(within(selector).getByRole("button", { name: "Close selector" })).toHaveFocus();

    await userEvent.keyboard("{Escape}");
    expect(chooser).toHaveFocus();
  });
});

it("空catalogをloadingやerrorと区別する", async () => {
  vi.stubGlobal("fetch", vi.fn((input: RequestInfo | URL) => {
    if (String(input) === "/api/items") return Promise.resolve(jsonResponse([]));
    return Promise.resolve(jsonResponse([]));
  }));

  render(<App />);

  expect(await screen.findByRole("heading", { name: "No items" })).toBeInTheDocument();
  vi.unstubAllGlobals();
});
