export interface SlackUser {
  id: string;
  username: string;
  displayName: string;
  avatarUrl?: string;
  isBot?: boolean;
}

export interface SlackReaction {
  name: string;
  userIds: string[];
  emoji?: string;
}

export interface SlackMessage {
  id: string;
  userId: string;
  text: string;
  ts: string; // epoch seconds as string
  reactions?: SlackReaction[];
  sentiment?: number; // -1 to 1
}

export interface SlackThread {
  id: string;
  rootMessageId: string;
  messages: SlackMessage[];
  lastActivityTs: string;
}

export interface SlackChannel {
  id: string;
  name: string;
  isPrivate?: boolean;
  memberUserIds?: string[];
  threads?: SlackThread[];
  lastFetchedTs?: string;
}

export interface SlackConnection {
  teamId: string;
  teamName: string;
  isConnected: boolean;
  botUserId?: string;
}


