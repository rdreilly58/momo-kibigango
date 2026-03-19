/**
 * Analytics tracking utilities for momo-kiji
 * Integrates with Google Analytics 4 (GA4)
 */

// Declare gtag globally
declare global {
  interface Window {
    gtag?: any;
  }
}

/**
 * Track external link clicks (GitHub, Discord, etc.)
 */
export const trackExternalClick = (destination: string, label: string) => {
  if (typeof window !== "undefined" && window.gtag) {
    window.gtag("event", "external_link_click", {
      destination: destination,
      label: label,
      timestamp: new Date().toISOString(),
    });
  }
};

/**
 * Track GitHub repository interactions
 */
export const trackGitHubAction = (action: string) => {
  if (typeof window !== "undefined" && window.gtag) {
    window.gtag("event", "github_interaction", {
      action: action,
      url: "https://github.com/ReillyDesignStudio/momo-kiji",
      timestamp: new Date().toISOString(),
    });
  }
};

/**
 * Track Discord server joins/invites
 */
export const trackDiscordJoin = () => {
  if (typeof window !== "undefined" && window.gtag) {
    window.gtag("event", "discord_join_click", {
      url: "https://discord.gg/DHRbKbzr",
      timestamp: new Date().toISOString(),
    });
  }
};

/**
 * Track documentation/research access
 */
export const trackDocAccess = (docPath: string) => {
  if (typeof window !== "undefined" && window.gtag) {
    window.gtag("event", "documentation_access", {
      doc_path: docPath,
      timestamp: new Date().toISOString(),
    });
  }
};

/**
 * Track user engagement (time on page, scrolling, etc.)
 */
export const trackEngagement = (metricName: string, value: number) => {
  if (typeof window !== "undefined" && window.gtag) {
    window.gtag("event", metricName, {
      value: value,
      timestamp: new Date().toISOString(),
    });
  }
};

/**
 * Track conversion events
 */
export const trackConversion = (conversionType: string, metadata?: Record<string, any>) => {
  if (typeof window !== "undefined" && window.gtag) {
    window.gtag("event", "conversion", {
      conversion_type: conversionType,
      ...metadata,
      timestamp: new Date().toISOString(),
    });
  }
};

/**
 * Track custom events (searchable in GA4)
 */
export const trackEvent = (eventName: string, eventData?: Record<string, any>) => {
  if (typeof window !== "undefined" && window.gtag) {
    window.gtag("event", eventName, {
      ...eventData,
      timestamp: new Date().toISOString(),
    });
  }
};

/**
 * Set user properties (for segmentation in GA4)
 */
export const setUserProperty = (propertyName: string, value: string) => {
  if (typeof window !== "undefined" && window.gtag) {
    window.gtag("set", {
      [propertyName]: value,
    });
  }
};

export default {
  trackExternalClick,
  trackGitHubAction,
  trackDiscordJoin,
  trackDocAccess,
  trackEngagement,
  trackConversion,
  trackEvent,
  setUserProperty,
};
