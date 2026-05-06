import RunwayML from '@runwayml/sdk';

const client = new RunwayML({
  apiKey: 'key_45f246eee25601b8a69a3a97dae03a11511f2a020bfe859ed8eec2a8aacf86bc0f687f9223800ab9e7c78df752feb4300f37984e2732464015c3d82802990494'
});

async function main() {
  console.log('🎬 Building AINL Commercial with Runway');
  console.log('=====================================\n');

  try {
    // Sequence 1: Chaos ($1,183)
    console.log('1️⃣  Generating Sequence 1: Chaos...');
    let task1 = await client.textToImage.create({
      promptText: "Neon pink text $1,183 flashing and morphing on pure black background. Intense glitch effects, chromatic aberration, cascading binary code. Psychedelic color shifts between hot pink, cyan, and purple. Very fast-paced, hypnotic, chaotic energy. Digital chaos.",
      model: "gen4_image_turbo",
      ratio: "1920:1080",
      seed: Math.floor(Math.random() * 1000000)
    }).waitForTaskOutput();

    console.log('   ✅ Sequence 1 complete');
    console.log('   Image URL:', task1.artifacts?.[0]?.url || 'N/A');

    // Sequence 2: Compilation grid
    console.log('\n2️⃣  Generating Sequence 2: Compilation...');
    let task2 = await client.textToImage.create({
      promptText: "Glowing neon grid materializing on black background. Text COMPILE appearing in large green neon letters. Checkmarks appearing one by one. Smooth, clean aesthetic. Cyan and green neon. Ethereal, calming energy building.",
      model: "gen4_image_turbo",
      ratio: "1920:1080",
      seed: Math.floor(Math.random() * 1000000)
    }).waitForTaskOutput();

    console.log('   ✅ Sequence 2 complete');
    console.log('   Image URL:', task2.artifacts?.[0]?.url || 'N/A');

    // Sequence 3: Proof (metrics)
    console.log('\n3️⃣  Generating Sequence 3: Proof...');
    let task3 = await client.textToImage.create({
      promptText: "Large glowing numbers 17, $29, 99.7% flowing and morphing on black background. Green neon glow. Data streams cascading. Metrics pulsing with confidence. Multiple colors cycling between green, cyan, and pink. Powerful, cinematic energy.",
      model: "gen4_image_turbo",
      ratio: "1920:1080",
      seed: Math.floor(Math.random() * 1000000)
    }).waitForTaskOutput();

    console.log('   ✅ Sequence 3 complete');
    console.log('   Image URL:', task3.artifacts?.[0]?.url || 'N/A');

    // Sequence 4: CTA (branding)
    console.log('\n4️⃣  Generating Sequence 4: CTA...');
    let task4 = await client.textToImage.create({
      promptText: "AINL logo materializing with radiating neon lines flowing outward. Text github.com/sbhooley/ainativelang appearing in bright cyan. Triumphant, clean energy. Pure neon cyan and white. Final triumphant moment.",
      model: "gen4_image_turbo",
      ratio: "1920:1080",
      seed: Math.floor(Math.random() * 1000000)
    }).waitForTaskOutput();

    console.log('   ✅ Sequence 4 complete');
    console.log('   Image URL:', task4.artifacts?.[0]?.url || 'N/A');

    console.log('\n=====================================');
    console.log('✅ All sequences generated!');
    console.log('\nNext steps:');
    console.log('1. Download the generated images');
    console.log('2. Create videos from each image');
    console.log('3. Assemble with audio design');
    console.log('4. Final commercial ready');

  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

main();
