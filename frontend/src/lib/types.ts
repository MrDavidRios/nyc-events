export interface Event {
  id: string;
  source_id: string;
  title: string;
  description: string | null;
  url: string;
  image_url: string | null;
  venue: string | null;
  address: string | null;
  category: string | null;
  tags: string[];
  start_date: string;
  end_date: string | null;
  start_time: string | null;
  end_time: string | null;
  is_free: boolean | null;
  price_range: string | null;
  last_updated: string;
}

export interface Source {
  id: string;
  name: string;
  url: string;
  type: string;
  category: string;
  scraper: string;
  favicon_url: string | null;
  enabled: boolean;
  notes: string;
}

export interface SourcesFile {
  sources: Source[];
}
