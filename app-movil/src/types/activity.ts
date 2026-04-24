export type ActivityStatus = 'pending' | 'done';

export type Activity = {
  id: string;
  title: string;
  dateLabel: string;
  timeLabel: string;
  place: string;
  status: ActivityStatus;
};
