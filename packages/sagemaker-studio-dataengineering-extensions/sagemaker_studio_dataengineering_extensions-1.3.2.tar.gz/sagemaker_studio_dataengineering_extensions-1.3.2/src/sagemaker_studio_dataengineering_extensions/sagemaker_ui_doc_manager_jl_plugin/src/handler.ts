import { SAGEMAKER_NB_EVENT, SAGEMAKER_MD_EVENT } from './constants';
import type { DocManagerFileEvent } from './models';

export const isExpressDomainEvent = (message: MessageEvent) => {
  const event = message.data as DocManagerFileEvent;
  return event.type === SAGEMAKER_MD_EVENT.MdExpressDomain && event.payload.value === true;
};

export const shouldOpenFile = (message: MessageEvent) => {
  const event = message.data as DocManagerFileEvent;
  return event.type === SAGEMAKER_NB_EVENT.OpenFileEvent && event.payload.path !== '';
};

export const shouldOpenUntitledFile = (message: MessageEvent) => {
  const event = message.data as DocManagerFileEvent;
  return event.type === SAGEMAKER_NB_EVENT.OpenUntitledFileEvent;
};

export const shouldOpenOrCreateFile = (message: MessageEvent) => {
  const event = message.data as DocManagerFileEvent;
  return event.type === SAGEMAKER_NB_EVENT.OpenOrCreateFileEvent;
};
