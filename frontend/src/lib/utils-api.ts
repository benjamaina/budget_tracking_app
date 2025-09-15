// Utility functions for API response handling

/**
 * Extracts data from a potentially paginated API response
 * Handles both paginated (with results) and non-paginated responses
 */
export const extractListData = <T>(response: any): T[] => {
  const data = response.data?.results || response.data;
  return Array.isArray(data) ? data : [];
};

/**
 * Extracts pagination metadata from API response
 */
export const extractPaginationMeta = (response: any) => {
  const { results, ...meta } = response.data || {};
  return {
    count: meta.count || 0,
    next: meta.next || null,
    previous: meta.previous || null,
    page_size: meta.page_size || 25,
  };
};

/**
 * Generates mock recent activities from existing data
 */
export const generateMockActivities = (pledges: any[], events: any[]) => {
  const activities = [];
  
  // Add recent pledges as activities
  pledges.slice(0, 3).forEach((pledge, index) => {
    const event = events.find(e => e.id === pledge.event);
    activities.push({
      id: `pledge-${pledge.id}`,
      type: 'pledge',
      title: pledge.is_fulfilled ? 'Payment received' : 'New pledge',
      description: `${pledge.name} ${pledge.is_fulfilled ? 'paid' : 'pledged'} for ${event?.name || 'Event'}`,
      amount: `KSh ${pledge.amount_pledged?.toLocaleString() || '0'}`,
      time: `${index + 1} hour${index === 0 ? '' : 's'} ago`,
      icon: 'DollarSign',
      status: pledge.is_fulfilled ? 'success' : 'warning'
    });
  });
  
  // Add recent events as activities
  events.slice(0, 2).forEach((event, index) => {
    activities.push({
      id: `event-${event.id}`,
      type: 'event',
      title: 'Event created',
      description: `${event.name} scheduled at ${event.venue}`,
      amount: `KSh ${event.total_budget?.toLocaleString() || '0'}`,
      time: `${index + 4} hours ago`,
      icon: 'Calendar',
      status: event.is_funded ? 'success' : 'neutral'
    });
  });
  
  return activities.slice(0, 5);
};