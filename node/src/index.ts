import { DATA } from "./data";
import { unpack } from "./unpack";
import type { Provider, Model, ProvidersData } from "./types";

export type { Provider, Model, ProvidersData, Cost, Limit, Modalities } from "./types";
export type { InputModality, OutputModality, Status, Interleaved, ModelProvider } from "./types";

let _data: ProvidersData | null = null;

async function getData(): Promise<ProvidersData> {
  if (!_data) {
    _data = await unpack(DATA);
  }
  return _data;
}

export async function providers(): Promise<Provider[]> {
  const data = await getData();
  return Object.values(data);
}

export async function getProviderInfo(providerId: string): Promise<Provider> {
  const data = await getData();
  const provider = data[providerId];
  if (!provider) {
    throw new Error(`Provider not found: ${providerId}`);
  }
  return provider;
}

export async function getModel(providerId: string, modelId: string): Promise<Model> {
  const provider = await getProviderInfo(providerId);
  const model = provider.models[modelId];
  if (!model) {
    throw new Error(`Model not found: ${modelId} in provider ${providerId}`);
  }
  return model;
}
