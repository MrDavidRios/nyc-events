"use client";

import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import type { Source } from "@/lib/types";

interface SettingsMenuProps {
  sources: Source[];
  enabledSources: Set<string>;
  onToggleSource: (sourceId: string) => void;
}

export function SettingsMenu({ sources, enabledSources, onToggleSource }: SettingsMenuProps) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="sm" aria-label="Settings">
          ⚙
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-64" align="end">
        <div className="space-y-1">
          <h4 className="font-medium text-sm mb-2">Sources</h4>
          {sources.map((source) => (
            <label
              key={source.id}
              className="flex items-center gap-2 py-1 cursor-pointer"
            >
              <Checkbox
                checked={enabledSources.has(source.id)}
                onCheckedChange={() => onToggleSource(source.id)}
              />
              {source.favicon_url && (
                <img src={source.favicon_url} alt="" className="w-4 h-4" />
              )}
              <span className="text-sm">{source.name}</span>
            </label>
          ))}
        </div>
      </PopoverContent>
    </Popover>
  );
}
