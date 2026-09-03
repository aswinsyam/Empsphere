/**
 * PageMeta.
 *
 * Lightweight per-page <title> and meta description updater. It mutates
 * document.head directly because the project does not use a router-aware
 * SEO library. Calling it on every public page keeps titles and meta
 * descriptions accurate for Razorpay merchant verification and search
 * engines.
 */

import { useEffect } from "react";

interface PageMetaProps {
  title: string;
  description: string;
}

export function PageMeta({ title, description }: PageMetaProps) {
  useEffect(() => {
    document.title = title;
    let tag = document.querySelector<HTMLMetaElement>('meta[name="description"]');
    if (!tag) {
      tag = document.createElement("meta");
      tag.name = "description";
      document.head.appendChild(tag);
    }
    tag.content = description;
  }, [title, description]);

  return null;
}
