/** Plain-language labels for editor fields. Field names come from the data model (href, video_url, ...). */
const OVERRIDES: Record<string, string> = {
  href: "Link",
  url: "YouTube video link",
  video_url: "Video link (YouTube)",
  cta_label: "Button label",
  cta_link: "Button link",
  form_endpoint: "Form service address",
  submit_label: "Send button label",
  show_form: "Show the contact form",
  show_business_info: "Show business details",
  show_contact: "Show phone and email",
  show_address: "Show the address",
  show_excerpt: "Show the summary",
  show_cover: "Show cover images",
  alt: "Description (alt text)",
  faq: "FAQ",
};

export function fieldLabel(name: string): string {
  const override = OVERRIDES[name];
  if (override) return override;
  const words = name.replace(/_/g, " ").trim();
  return words.charAt(0).toUpperCase() + words.slice(1);
}
