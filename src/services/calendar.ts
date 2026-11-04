import { CulturalEvent } from '../types';

function formatToIcsDate(dateStr: string, timeStr: string = '00:00'): string {
  const [year, month, day] = dateStr.split('-');
  const [hours, minutes] = timeStr.split(':');
  // Format: YYYYMMDDTHHMMSS
  return `${year}${month}${day}T${hours || '00'}${minutes || '00'}00`;
}

export function generateGoogleCalendarUrl(event: CulturalEvent): string {
  const startIso = formatToIcsDate(event.start_date, event.start_time);
  const endIso = formatToIcsDate(
    event.end_date || event.start_date,
    event.end_time || '23:00'
  );

  const title = encodeURIComponent(event.title);
  const details = encodeURIComponent(
    `${event.short_description}\n\nOrganiza: ${event.organizer_name}\nFuente oficial: ${event.source_url}\nDescubierto en Evenjoy: https://evenjoy.co/evento/${event.slug}`
  );
  const location = encodeURIComponent(`${event.venue_name}, ${event.address}, ${event.municipality}, Antioquia`);

  return `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&dates=${startIso}/${endIso}&details=${details}&location=${location}`;
}

export function downloadIcsFile(event: CulturalEvent) {
  const startIso = formatToIcsDate(event.start_date, event.start_time);
  const endIso = formatToIcsDate(
    event.end_date || event.start_date,
    event.end_time || '23:00'
  );

  const icsContent = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//Evenjoy Antioquia//Agenda Cultural//ES',
    'CALSCALE:GREGORIAN',
    'METHOD:PUBLISH',
    'BEGIN:VEVENT',
    `UID:${event.event_id}@evenjoy.co`,
    `DTSTAMP:${startIso}Z`,
    `DTSTART:${startIso}`,
    `DTEND:${endIso}`,
    `SUMMARY:${event.title.replace(/[,;]/g, ' ')}`,
    `DESCRIPTION:${event.short_description.replace(/\n/g, ' ')}`,
    `LOCATION:${event.venue_name}, ${event.municipality}, Antioquia`,
    `URL:https://evenjoy.co/evento/${event.slug}`,
    'STATUS:CONFIRMED',
    'END:VEVENT',
    'END:VCALENDAR',
  ].join('\r\n');

  const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `${event.slug}.ics`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}
