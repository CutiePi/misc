// run: node csvGeneratorScrumpy.js > scrumpy.csv

const copyPaste = ``;
const match = new RegExp(/\/RG|SG-[0-9]{4,6}/);
const values = copyPaste.split('\n')
  .filter(line => match.exec(line) !== null)
  .map(line => match.exec(line)[0])
  .map(card => `,,${card},,,,,,`)
  .join('\n');
console.log(`avatar,description,key,link,preset,status,statusAvatar,storyPoints,summary\n${values}`);