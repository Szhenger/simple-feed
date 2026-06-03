import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/common/Layout';
import { WorkspaceBoard } from './components/workspace/WorkspaceBoard';

const queryClient = new QueryClient({
  defaultOptions: { queries: { refetchOnWindowFocus: false } },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <Layout>
        <WorkspaceBoard />
      </Layout>
    </QueryClientProvider>
  );
};

export default App;
