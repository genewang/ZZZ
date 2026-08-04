export const navLinks = [
  { href: "#kits", label: "Kits" },
  { href: "#create", label: "Create" },
  { href: "#how", label: "How it works" },
  { href: "#system", label: "System" },
  { href: "#churches", label: "Churches" },
] as const;

export const howSteps = [
  {
    step: "1",
    title: "Pick a kit line",
    body: "Choose by age — from first Bible stories to teen creation labs.",
  },
  {
    step: "2",
    title: "Open your monthly box",
    body: "Storybook, craft, character cards, and a Create prompt arrive ready to go.",
  },
  {
    step: "3",
    title: "Make it yours",
    body: "Build the craft, then shape a printable Bible scene in Create Studio — with a parent tap to approve.",
  },
] as const;

export type KitLine = {
  id: string;
  name: string;
  ages: string;
  focus: string;
  accent: string;
  blurb: string;
  includes: string[];
};

export const kitLines: KitLine[] = [
  {
    id: "seedling",
    name: "Seedling",
    ages: "Ages 3–5",
    focus: "Wonder & wonder tales",
    accent: "#3a6b52",
    blurb: "Short parable play, soft crafts, and an Avarta guide that waits for a parent.",
    includes: ["Board storybook", "Sensory craft", "2 character cards", "Bedtime prompt"],
  },
  {
    id: "sprout",
    name: "Sprout",
    ages: "Ages 5–8",
    focus: "Stories that stick",
    accent: "#c4922a",
    blurb: "Monthly Bible arcs with hands-on builds — arks, slings, mustard seeds that grow into family ritual.",
    includes: ["Illustrated storybook", "Build kit", "4 character cards", "Create Studio prompt"],
  },
  {
    id: "branch",
    name: "Branch",
    ages: "Ages 8–12",
    focus: "Create & inquire",
    accent: "#2a6f8f",
    blurb: "Deeper questions, richer crafts, and AI scenes kids design under clear guardrails.",
    includes: ["Chapter story", "Advanced craft", "Scene cards", "Printable 3D challenge"],
  },
  {
    id: "cedar",
    name: "Cedar",
    ages: "Ages 12–16",
    focus: "Faith & craftsmanship",
    accent: "#8b4d2b",
    blurb: "Teen devotion meets maker lab — character packs, legacy interviews, church volunteer modes.",
    includes: ["Devotional journal", "Maker project", "Legacy interview kit", "Church share pack"],
  },
];

export const createModes = [
  { id: "text", label: "Story to 3D" },
  { id: "sketch", label: "Sketch to 3D" },
] as const;

export const createPresets = [
  {
    prompt: "Noah’s ark resting on a misty mountain, kid-friendly, printable",
    title: "Noah’s Ark",
    tag: "Genesis",
  },
  {
    prompt: "David’s sling and five smooth stones, simple toy style",
    title: "David’s Sling",
    tag: "1 Samuel",
  },
  {
    prompt: "Mustard seed tree with glowing birds, parable scene",
    title: "Mustard Tree",
    tag: "Matthew",
  },
  {
    prompt: "Good Samaritan helping on a dusty road, gentle characters",
    title: "Good Samaritan",
    tag: "Luke",
  },
] as const;

export const boxContents = [
  {
    title: "Storybook",
    body: "Age-fit scripture narrative designed for read-aloud and reenactment.",
  },
  {
    title: "Hands-on craft",
    body: "All materials included — no last-minute store run between dinner and bedtime.",
  },
  {
    title: "Character cards",
    body: "Collectible figures that unlock Create Studio scenes and Avarta prompts.",
  },
  {
    title: "Family prompt",
    body: "One conversation starter for parents, kids, and grandparents on the same theme.",
  },
] as const;

export const trustPoints = [
  {
    title: "Parent-gated AI",
    body: "Avarta and Create never run unsupervised. Every reply and model needs an Approve tap.",
  },
  {
    title: "Zero-Trust by design",
    body: "Family stories and faith data stay sealed. Agents are jailed — they can’t wander off-script.",
  },
  {
    title: "Born printable",
    body: "Create Studio models are tuned for home printers and classroom makerspaces — watertight first.",
  },
] as const;

export const testimonials = [
  {
    quote:
      "Saturday used to be screen chaos. Now Maya asks for ark night — craft first, then she prints the animals she designed.",
    name: "Priya M.",
    role: "Parent · Sprout kit",
  },
  {
    quote:
      "Our volunteers finally have a coherent monthly arc. The AI scene builder is the spark; the kit is the backbone.",
    name: "Pastor Ellis",
    role: "Church plant · Houston",
  },
  {
    quote:
      "I recorded Psalm 23 for my grandkids. StoryKeeper turned it into a keepsake they still ask for at bedtime.",
    name: "Ruth K.",
    role: "Legacy tier",
  },
] as const;

export const faqs = [
  {
    q: "How does a kits4kid subscription work?",
    a: "Pick a kit line by age. Each month a box arrives with a storybook, craft, character cards, and a Create Studio prompt. Cancel or pause anytime before the next ship date.",
  },
  {
    q: "Is the AI safe for kids?",
    a: "Yes — Create Studio and Avarta are parent-gated. Nothing generates or speaks until a parent Approves. Content stays inside a faith-formation guardrail set you can review.",
  },
  {
    q: "Do I need a 3D printer?",
    a: "No. You can view models in-app, export for a school makerspace, or order a printed figure shipped to your door.",
  },
  {
    q: "Can churches and schools subscribe?",
    a: "Yes. Church & school licenses include classroom packs, volunteer guides, and shared Create seats under the same Zero-Trust controls.",
  },
] as const;

export const churchPoints = [
  {
    title: "Classroom packs",
    body: "Same monthly arc for every small group — kits plus shared Create prompts.",
  },
  {
    title: "Volunteer-ready",
    body: "Guides assume busy helpers, not seminary grads. Setup under ten minutes.",
  },
  {
    title: "Licensed safely",
    body: "Doctrine-aware evals and parent/church admin controls on every agent.",
  },
] as const;
