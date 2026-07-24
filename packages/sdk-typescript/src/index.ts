/** Praevis TypeScript SDK stub (working codename). */

export const SDK_VERSION = "0.1.0";

export type HealthResponse = {
  status: string;
  service: string;
};

export class PraevisClient {
  constructor(private readonly baseUrl: string = "http://localhost:8000") {}

  async health(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseUrl.replace(/\/$/, "")}/health`);
    if (!response.ok) {
      throw new Error(`health check failed: ${response.status}`);
    }
    return (await response.json()) as HealthResponse;
  }
}
