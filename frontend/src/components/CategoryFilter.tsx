"use client";

import { Badge } from "@/components/ui/badge";

const CATEGORIES = [
  { id: "all", label: "All" },
  { id: "museum", label: "Museum" },
  { id: "outdoor", label: "Outdoor" },
  { id: "film", label: "Film" },
  { id: "theater", label: "Theater" },
  { id: "performing-arts", label: "Performing Arts" },
];

interface CategoryFilterProps {
  activeCategories: Set<string>;
  onChange: (categories: Set<string>) => void;
}

export function CategoryFilter({ activeCategories, onChange }: CategoryFilterProps) {
  function handleClick(categoryId: string) {
    if (categoryId === "all") {
      onChange(new Set(["all"]));
      return;
    }

    const next = new Set(activeCategories);
    next.delete("all");

    if (next.has(categoryId)) {
      next.delete(categoryId);
    } else {
      next.add(categoryId);
    }

    if (next.size === 0) {
      onChange(new Set(["all"]));
    } else {
      onChange(next);
    }
  }

  return (
    <div className="flex flex-wrap gap-2 py-2">
      {CATEGORIES.map((cat) => {
        const isActive = activeCategories.has(cat.id);
        return (
          <Badge
            key={cat.id}
            variant={isActive ? "default" : "outline"}
            className="cursor-pointer select-none"
            onClick={() => handleClick(cat.id)}
          >
            {cat.label}
          </Badge>
        );
      })}
    </div>
  );
}
