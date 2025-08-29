import ProviderCard from './ProviderCard';

const providers = [
  {
    id: 'openai',
    name: 'OpenAI',
    capabilities: [
      { name: 'LLM' },
      { name: 'TEXT EMBEDDING' },
      { name: 'SPEECH2TEXT' },
      { name: 'MODERATION' },
      { name: 'TTS' }
    ],
    tokenLimit: 200,
    tokenUsed: 200,
    status: 'disconnected' as const,
    hasApiKey: false
  },
  {
    id: 'anthropic',
    name: 'ANTHROPIC',
    capabilities: [
      { name: 'LLM' }
    ],
    tokenLimit: 0,
    tokenUsed: 0,
    status: 'disconnected' as const,
    hasApiKey: false
  },
  {
    id: 'siliconflow',
    name: '硅基流动',
    capabilities: [
      { name: 'LLM' },
      { name: 'TEXT EMBEDDING' },
      { name: 'RERANK' },
      { name: 'SPEECH2TEXT' },
      { name: 'TTS' }
    ],
    status: 'connected' as const,
    hasApiKey: true
  },
  {
    id: 'deepseek',
    name: '深度求索',
    capabilities: [
      { name: 'LLM' }
    ],
    status: 'connected' as const,
    hasApiKey: true
  }
];

export default function ProviderList() {
  return (
    <div className="p-6">
      <div className="space-y-4">
        {providers.map((provider) => (
          <ProviderCard key={provider.id} provider={provider} />
        ))}
      </div>
    </div>
  );
}