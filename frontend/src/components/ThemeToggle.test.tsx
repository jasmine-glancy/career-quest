import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ThemeToggle } from "./ThemeToggle";

function mockMatchMedia(matches: boolean) {
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    configurable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches,
      media: query,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    })),
  });
}

describe("ThemeToggle", () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.removeAttribute("data-theme");
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("offers to switch to dark when the system prefers light and nothing is stored", () => {
    mockMatchMedia(false);
    render(<ThemeToggle />);

    expect(screen.getByRole("button", { name: "Switch to dark mode" })).toBeInTheDocument();
  });

  it("offers to switch to light when the system prefers dark", () => {
    mockMatchMedia(true);
    render(<ThemeToggle />);

    expect(screen.getByRole("button", { name: "Switch to light mode" })).toBeInTheDocument();
  });

  it("a stored preference wins over the system preference", () => {
    mockMatchMedia(false); // system says light
    localStorage.setItem("theme", "dark"); // user previously chose dark
    render(<ThemeToggle />);

    expect(screen.getByRole("button", { name: "Switch to light mode" })).toBeInTheDocument();
  });

  it("clicking sets data-theme on <html> and persists the choice", async () => {
    mockMatchMedia(false);
    const user = userEvent.setup();
    render(<ThemeToggle />);

    await user.click(screen.getByRole("button", { name: "Switch to dark mode" }));

    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");
    expect(localStorage.getItem("theme")).toBe("dark");
    expect(screen.getByRole("button", { name: "Switch to light mode" })).toBeInTheDocument();
  });

  it("clicking twice returns to light", async () => {
    mockMatchMedia(false);
    const user = userEvent.setup();
    render(<ThemeToggle />);

    const button = screen.getByRole("button");
    await user.click(button);
    await user.click(button);

    expect(document.documentElement.getAttribute("data-theme")).toBe("light");
    expect(localStorage.getItem("theme")).toBe("light");
  });

  it("decorative icons are hidden from assistive technology", () => {
    mockMatchMedia(false);
    render(<ThemeToggle />);

    const svg = document.querySelector("svg");
    expect(svg).toHaveAttribute("aria-hidden", "true");
  });
});
