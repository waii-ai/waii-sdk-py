import React from 'react';
import { Redirect } from '@docusaurus/router';

function Home() {
  return <Redirect to="/docs/intro" />;
}

export default Home;
