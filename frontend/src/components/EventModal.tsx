"use client";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import type { Event, Source } from "@/lib/types";

interface EventModalProps {
  event: Event | null;
  open: boolean;
  onClose: () => void;
  isInterested: boolean;
  onToggleInterested: () => void;
  source?: Source;
}

function formatDate(date: string): string {
  return new Date(date + "T00:00:00").toLocaleDateString("en-US", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function formatTime(time: string): string {
  const [h, m] = time.split(":");
  const hour = parseInt(h, 10);
  const ampm = hour >= 12 ? "PM" : "AM";
  const hour12 = hour % 12 || 12;
  return `${hour12}:${m} ${ampm}`;
}

export function EventModal({
  event,
  open,
  onClose,
  isInterested,
  onToggleInterested,
  source,
}: EventModalProps) {
  if (!event) return null;

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="text-xl">{event.title}</DialogTitle>
        </DialogHeader>

        <div className="space-y-3">
          <div className="text-sm text-muted-foreground">
            <p>{formatDate(event.start_date)}</p>
            {event.start_time && (
              <p>
                {formatTime(event.start_time)}
                {event.end_time && ` – ${formatTime(event.end_time)}`}
              </p>
            )}
            {event.end_date && event.end_date !== event.start_date && (
              <p>Through {formatDate(event.end_date)}</p>
            )}
          </div>

          {event.venue && (
            <div>
              <p className="font-medium">{event.venue}</p>
              {event.address && (
                <p className="text-sm text-muted-foreground">{event.address}</p>
              )}
            </div>
          )}

          {event.description && (
            <p className="text-sm leading-relaxed">{event.description}</p>
          )}

          {source && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              {source.favicon_url && (
                <img
                  src={source.favicon_url}
                  alt=""
                  className="w-4 h-4"
                />
              )}
              <span>{source.name}</span>
            </div>
          )}

          {event.price_range && (
            <p className="text-sm">{event.price_range}</p>
          )}
          {event.is_free && (
            <p className="text-sm font-medium text-green-600">Free!</p>
          )}

          <div className="flex gap-2 pt-2">
            <Button
              variant={isInterested ? "default" : "outline"}
              size="sm"
              onClick={onToggleInterested}
            >
              {isInterested ? "★ Interested" : "☆ Mark Interested"}
            </Button>
            <Button variant="outline" size="sm" asChild>
              <a href={event.url} target="_blank" rel="noopener noreferrer">
                View on site ↗
              </a>
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
