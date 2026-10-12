import { expect, test } from '@playwright/test';

test('search real neurons, recover shared anatomy, inspect synapses and expand partners',async({page})=>{
  test.setTimeout(120000);
  const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('/');
  await page.getByRole('button',{name:'Brain',exact:true}).click();
  await page.getByRole('button',{name:'Real circuit anatomy',exact:true}).click();
  const atlas=page.getByRole('region',{name:'Real circuit anatomy'});
  await expect(atlas).toContainText('165,122 Traced neurons',{timeout:30000});
  await expect(page.getByTestId('neuron-search-count')).toContainText('11 matches');
  await page.getByRole('button',{name:'Load recovery five',exact:true}).click();
  await expect(page.getByTestId('circuit-loaded')).toHaveText('5/5 skeletons loaded',{timeout:60000});
  await expect(page.getByTestId('circuit-edge-count')).not.toContainText('Select neurons');
  await page.getByTestId('circuit-canvas').screenshot({path:test.info().outputPath('recovered-anatomy.png')});
  // Source-specific strongest downstream partner; validated against the official flat table.
  await page.getByRole('button',{name:'Expand to neuron 21763',exact:true}).click();
  await expect(page.getByRole('button',{name:'Remove neuron 21763',exact:true})).toBeVisible();
  await page.getByRole('button',{name:'Inspect synapses 71254 to 21763',exact:true}).click();
  await expect(page.getByTestId('synapse-count')).toContainText('86 shown / 86 matching',{timeout:30000});
  await page.getByLabel('Synapse confidence',{exact:true}).fill('0.95');
  await expect(page.getByTestId('synapse-count')).toContainText('13 shown / 13 matching');
  await page.getByLabel('Partner direction').selectOption('upstream');
  await expect(page.getByLabel('Connected partners')).toContainText('71254');
  await page.getByLabel('Search real neurons').fill('Quasimodo');
  await page.getByRole('button',{name:'Search neurons',exact:true}).click();
  await expect(page.getByLabel('Neuron search results')).toContainText('GNG042');
  await page.getByRole('button',{name:'Clear neurons',exact:true}).click();
  await expect(page.getByTestId('circuit-loaded')).toHaveText('0/0 skeletons loaded');
  await page.setViewportSize({width:390,height:844});
  await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.screenshot({path:test.info().outputPath('circuit-mobile.png'),fullPage:true});
  await page.getByRole('button',{name:'← Back to fly',exact:true}).click();
  await expect(page.locator('[data-world-viewport]')).toBeVisible();
  expect(errors).toEqual([]);
});
