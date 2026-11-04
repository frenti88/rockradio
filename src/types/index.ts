export type Subregion = 
  | 'Valle de Aburrá'
  | 'Oriente'
  | 'Suroeste'
  | 'Occidente'
  | 'Norte'
  | 'Nordeste'
  | 'Bajo Cauca'
  | 'Magdalena Medio'
  | 'Urabá';

export type EventCategory = 
  | 'Música'
  | 'Fiestas'
  | 'Arte'
  | 'Teatro'
  | 'Cine'
  | 'Gastronomía'
  | 'Ferias'
  | 'Talleres'
  | 'Literatura'
  | 'Patrimonio'
  | 'Familia'
  | 'Naturaleza';

export type EventFormat = 'in_person' | 'outdoor' | 'hybrid';

export type AudienceType = 'all_ages' | 'family' | 'adults' | 'kids' | 'youth';

export type PriceType = 'free' | 'paid' | 'donation';

export type EventStatus = 
  | 'ACTIVE' 
  | 'CANCELLED' 
  | 'POSTPONED' 
  | 'SOLD_OUT' 
  | 'DATE_CHANGED' 
  | 'EXPIRED' 
  | 'UNVERIFIED';

export type SourceType = 
  | 'government' 
  | 'cultural_center' 
  | 'compensation_box' 
  | 'ticketing' 
  | 'community' 
  | 'independent'
  | 'university';

export interface SecondarySource {
  source_name: string;
  source_url: string;
  source_type: SourceType;
  detected_at: string;
}

export interface CulturalEvent {
  event_id: string;
  title: string;
  slug: string;
  short_description: string;
  description: string;
  start_date: string; // YYYY-MM-DD
  end_date: string;   // YYYY-MM-DD
  start_time: string; // HH:mm
  end_time?: string;  // HH:mm
  timezone: string;   // America/Bogota
  municipality: string; // ej. Jardín, Jericó, Medellín
  subregion: Subregion;
  venue_name: string;
  address: string;
  latitude: number;
  longitude: number;
  event_format: EventFormat;
  category: EventCategory;
  subcategory?: string;
  audience: AudienceType;
  price_type: PriceType;
  price_from: number; // 0 if free
  price_to?: number;
  currency: 'COP';
  registration_required: boolean;
  image_url: string;
  image_fallback_palette?: [string, string];
  organizer_name: string;
  organizer_url?: string;
  source_name: string;
  source_url: string;
  source_type: SourceType;
  source_published_at: string;
  first_detected_at: string;
  last_verified_at: string; // ISO or relative
  status: EventStatus;
  tags: string[];
  is_featured?: boolean;
  is_worth_the_trip?: boolean;
  secondary_sources?: SecondarySource[];
  created_at: string;
  updated_at: string;
}

export interface MunicipalityData {
  name: string;
  slug: string;
  subregion: Subregion;
  department: 'Antioquia';
  description: string;
  hero_image: string;
  altitude_m: number;
  distance_from_medellin_km: number;
  travel_time_approx: string;
  latitude: number;
  longitude: number;
  cultural_tags: string[];
  signature_tradition: string;
  climate?: string;
}

export interface SourceEntity {
  id: string;
  name: string;
  type: SourceType;
  url: string;
  municipality?: string;
  subregion?: Subregion;
  status: 'active' | 'warning' | 'error';
  ingestion_method: 'crawler' | 'rss' | 'api' | 'ai_agent' | 'manual';
  last_sync: string;
  last_successful_sync: string;
  reliability_score: number; // 0 to 100%
  total_events_ingested: number;
  active_events_count: number;
}

export interface FilterState {
  dateRange: 'all' | 'today' | 'tomorrow' | 'this_weekend' | 'this_week' | 'next_weekend' | 'custom';
  customDate?: string;
  municipality: string | 'all';
  subregion: Subregion | 'all';
  category: EventCategory | 'all';
  priceType: 'all' | 'free' | 'paid';
  audience: AudienceType | 'all';
  format: EventFormat | 'all';
  searchQuery: string;
  onlyVerified: boolean;
  nearMe: boolean;
  userCoords?: { latitude: number; longitude: number };
  maxDistanceKm?: number;
}

export interface DeduplicationGroup {
  canonical_event: CulturalEvent;
  detected_duplicates: Array<{
    source_name: string;
    source_url: string;
    source_type: SourceType;
    similarity_score: number;
    detected_title: string;
    detected_venue: string;
    detected_at: string;
  }>;
}
