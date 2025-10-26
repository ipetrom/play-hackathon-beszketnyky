import type { Report, ReportDetail } from "./types"

export const mockReports: Report[] = [
  {
    id: "1",
    title: "Orange Polska announces new 5G network expansion",
    status: "active",
    createdAt: "2024-10-24T10:30:00Z",
    hasDiff: true,
    category: "Telecom",
    impact: {
      level: "High",
      description: "Significant infrastructure investment affecting market competition"
    },
    date: "2024-10-24T10:30:00Z",
    source: "Orange Polska",
    summary: "Orange Polska has announced a major expansion of its 5G network coverage across Poland, with plans to reach 80% of the population by end of 2025.",
    url: "https://orange.pl/news/5g-expansion",
    tags: ["5G", "infrastructure", "Orange", "network"]
  },
  {
    id: "2", 
    title: "Play introduces new unlimited data plans",
    status: "active",
    createdAt: "2024-10-24T14:15:00Z",
    hasDiff: false,
    category: "Telecom",
    impact: {
      level: "Medium",
      description: "Pricing changes that may affect competitor strategies"
    },
    date: "2024-10-24T14:15:00Z",
    source: "Play",
    summary: "Play has launched new unlimited data plans starting from 49 PLN/month, significantly undercutting current market prices.",
    url: "https://play.pl/plans/unlimited",
    tags: ["pricing", "data plans", "Play", "unlimited"]
  },
  {
    id: "3",
    title: "Plus network maintenance scheduled for November",
    status: "active",
    createdAt: "2024-10-24T16:45:00Z",
    hasDiff: false,
    category: "Telecom", 
    impact: {
      level: "Low",
      description: "Planned maintenance with minimal service impact"
    },
    date: "2024-10-24T16:45:00Z",
    source: "Plus",
    summary: "Plus has announced scheduled network maintenance for November 5-7, 2024, which may cause temporary service disruptions.",
    url: "https://plus.pl/maintenance",
    tags: ["maintenance", "Plus", "network", "scheduled"]
  },
  {
    id: "4",
    title: "T-Mobile Poland reports Q3 2024 financial results",
    status: "active",
    createdAt: "2024-10-24T09:20:00Z",
    hasDiff: false,
    category: "Financial",
    impact: {
      level: "Medium", 
      description: "Financial performance indicators affecting market sentiment"
    },
    date: "2024-10-24T09:20:00Z",
    source: "T-Mobile Poland",
    summary: "T-Mobile Poland reported strong Q3 2024 results with revenue growth of 8.5% year-over-year and subscriber base expansion.",
    url: "https://t-mobile.pl/investor-relations/q3-2024",
    tags: ["financial", "Q3", "T-Mobile", "revenue", "subscribers"]
  },
  {
    id: "5",
    title: "New EU regulations on telecom roaming charges",
    status: "active",
    createdAt: "2024-10-24T11:00:00Z",
    hasDiff: false,
    category: "Regulatory",
    impact: {
      level: "Critical",
      description: "New regulations that will significantly impact pricing and business models"
    },
    date: "2024-10-24T11:00:00Z", 
    source: "EU Commission",
    summary: "The European Commission has announced new regulations limiting roaming charges within the EU, effective January 2025.",
    url: "https://ec.europa.eu/roaming-regulations",
    tags: ["EU", "regulations", "roaming", "pricing", "compliance"]
  },
  {
    id: "6",
    title: "Vectra launches fiber internet in Warsaw",
    status: "active",
    createdAt: "2024-10-24T13:30:00Z",
    hasDiff: false,
    category: "Telecom",
    impact: {
      level: "Medium",
      description: "New market entrant increasing competition in Warsaw area"
    },
    date: "2024-10-24T13:30:00Z",
    source: "Vectra",
    summary: "Vectra has launched high-speed fiber internet services in Warsaw, offering speeds up to 1 Gbps for residential customers.",
    url: "https://vectra.pl/warsaw-fiber",
    tags: ["fiber", "Vectra", "Warsaw", "internet", "competition"]
  },
  {
    id: "7",
    title: "UKE announces spectrum auction for 2025",
    status: "active",
    createdAt: "2024-10-24T15:00:00Z",
    hasDiff: false,
    category: "Regulatory",
    impact: {
      level: "High",
      description: "Spectrum allocation that will affect 5G deployment strategies"
    },
    date: "2024-10-24T15:00:00Z",
    source: "UKE",
    summary: "The Office of Electronic Communications (UKE) has announced a spectrum auction for 3.5 GHz band, scheduled for Q2 2025.",
    url: "https://uke.gov.pl/spectrum-auction-2025",
    tags: ["spectrum", "auction", "UKE", "5G", "3.5GHz"]
  },
  {
    id: "8",
    title: "Cyfrowy Polsat reports subscriber growth",
    status: "active",
    createdAt: "2024-10-24T12:15:00Z",
    hasDiff: false,
    category: "Financial",
    impact: {
      level: "Low",
      description: "Positive subscriber metrics indicating market growth"
    },
    date: "2024-10-24T12:15:00Z",
    source: "Cyfrowy Polsat",
    summary: "Cyfrowy Polsat reported a 3.2% increase in mobile subscribers in Q3 2024, reaching 2.1 million active users.",
    url: "https://cyfrowypolsat.pl/investor-relations",
    tags: ["subscribers", "growth", "Cyfrowy Polsat", "mobile"]
  }
]

export const mockReportDetails: ReportDetail[] = [
  {
    id: "1",
    title: "Orange Polska announces new 5G network expansion",
    category: "Telecom",
    impact: {
      level: "High",
      description: "Significant infrastructure investment affecting market competition",
      score: 8.5
    },
    createdAt: "2024-10-24T10:30:00Z",
    deadline: "2024-11-15T00:00:00Z",
    summary: "Orange Polska has announced a major expansion of its 5G network coverage across Poland, with plans to reach 80% of the population by end of 2025. This represents a €2.3 billion investment in network infrastructure.",
    body: `
      <h2>Executive Summary</h2>
      <p>Orange Polska has unveiled ambitious plans to significantly expand its 5G network coverage across Poland, marking one of the largest telecommunications infrastructure investments in the country's history.</p>
      
      <h3>Key Investment Details</h3>
      <ul>
        <li><strong>Total Investment:</strong> €2.3 billion over 3 years</li>
        <li><strong>Coverage Target:</strong> 80% of Polish population by end of 2025</li>
        <li><strong>New Base Stations:</strong> 15,000 additional 5G sites</li>
        <li><strong>Technology:</strong> Standalone 5G (SA) architecture</li>
      </ul>
      
      <h3>Market Impact</h3>
      <p>This expansion positions Orange as a leading 5G provider in Poland, directly competing with T-Mobile Poland and Plus. The investment is expected to:</p>
      <ul>
        <li>Accelerate 5G adoption across rural and suburban areas</li>
        <li>Enable new IoT and smart city applications</li>
        <li>Support Poland's digital transformation goals</li>
        <li>Create approximately 3,000 new jobs in network deployment</li>
      </ul>
      
      <h3>Technical Specifications</h3>
      <p>The new 5G network will utilize:</p>
      <ul>
        <li><strong>Frequency Bands:</strong> 3.5 GHz (primary), 700 MHz (coverage)</li>
        <li><strong>Peak Speeds:</strong> Up to 1 Gbps download, 100 Mbps upload</li>
        <li><strong>Latency:</strong> Sub-10ms for ultra-reliable applications</li>
        <li><strong>Network Slicing:</strong> Support for enterprise and consumer use cases</li>
      </ul>
      
      <h3>Regulatory Considerations</h3>
      <p>The expansion is subject to approval from the Office of Electronic Communications (UKE) and must comply with EU 5G security guidelines. Orange has already secured necessary spectrum licenses and is working closely with local authorities for site approvals.</p>
    `,
    entities: ["Orange Polska", "T-Mobile Poland", "Plus", "UKE", "Polish Government"],
    sources: [
      {
        label: "Orange Polska Press Release",
        url: "https://orange.pl/news/5g-expansion"
      },
      {
        label: "UKE Spectrum Allocation",
        url: "https://uke.gov.pl/spectrum-5g"
      },
      {
        label: "EU 5G Guidelines",
        url: "https://ec.europa.eu/5g-security"
      }
    ],
    metadataJson: JSON.stringify({
      id: "1",
      title: "Orange Polska announces new 5G network expansion",
      category: "Telecom",
      impact: { level: "High", score: 8.5 },
      entities: ["Orange Polska", "T-Mobile Poland", "Plus", "UKE", "Polish Government"],
      sources: 3,
      createdAt: "2024-10-24T10:30:00Z",
      deadline: "2024-11-15T00:00:00Z"
    }, null, 2),
    hasDiff: true,
    diff: {
      page: "https://orange.pl/plans/5g-coverage",
      before: {
        title: "5G Coverage Map - Current",
        content: "Orange 5G is available in major cities: Warsaw, Krakow, Gdansk, Wroclaw, Poznan",
        features: ["Urban coverage", "City centers", "Major highways"]
      },
      after: {
        title: "5G Coverage Map - Planned 2025",
        content: "Orange 5G will cover 80% of Poland including rural areas, small towns, and industrial zones",
        features: ["Nationwide coverage", "Rural areas", "Industrial zones", "Smart cities"]
      },
      changes: [
        {
          type: "modified",
          field: "coverage_area",
          before: "Major cities only",
          after: "80% of Poland"
        },
        {
          type: "added",
          field: "rural_coverage",
          before: undefined,
          after: "Rural and suburban areas included"
        },
        {
          type: "modified",
          field: "population_coverage",
          before: "30%",
          after: "80%"
        }
      ],
      highlights: [
        "+50% population coverage",
        "+Rural area coverage",
        "+Industrial zones",
        "+Smart city integration",
        "-Urban-only limitation"
      ]
    }
  },
  {
    id: "2",
    title: "Play introduces new unlimited data plans",
    category: "Telecom",
    impact: {
      level: "Medium",
      description: "Pricing changes that may affect competitor strategies",
      score: 6.2
    },
    createdAt: "2024-10-24T14:15:00Z",
    summary: "Play has launched new unlimited data plans starting from 49 PLN/month, significantly undercutting current market prices and potentially triggering a price war in the Polish telecom market.",
    body: `
      <h2>Pricing Revolution in Polish Telecom</h2>
      <p>Play has disrupted the Polish telecommunications market with the introduction of aggressive unlimited data plans that are 30-40% cheaper than current market offerings.</p>
      
      <h3>New Plan Structure</h3>
      <table>
        <tr>
          <th>Plan</th>
          <th>Price</th>
          <th>Data</th>
          <th>Features</th>
        </tr>
        <tr>
          <td>Play Unlimited Basic</td>
          <td>49 PLN/month</td>
          <td>Unlimited</td>
          <td>5G, 100 Mbps speed cap</td>
        </tr>
        <tr>
          <td>Play Unlimited Plus</td>
          <td>69 PLN/month</td>
          <td>Unlimited</td>
          <td>5G, 300 Mbps speed cap, EU roaming</td>
        </tr>
        <tr>
          <td>Play Unlimited Premium</td>
          <td>99 PLN/month</td>
          <td>Unlimited</td>
          <td>5G, No speed cap, Global roaming</td>
        </tr>
      </table>
      
      <h3>Market Response Expected</h3>
      <p>Industry analysts predict that competitors will be forced to respond:</p>
      <ul>
        <li><strong>T-Mobile Poland:</strong> Likely to introduce competitive unlimited plans</li>
        <li><strong>Plus:</strong> May reduce prices on existing unlimited offerings</li>
        <li><strong>Orange:</strong> Could launch counter-offers to retain market share</li>
      </ul>
      
      <h3>Financial Impact</h3>
      <p>Play's aggressive pricing strategy is expected to:</p>
      <ul>
        <li>Reduce average revenue per user (ARPU) across the industry</li>
        <li>Accelerate customer acquisition for Play</li>
        <li>Force competitors to invest more in network efficiency</li>
        <li>Potentially trigger regulatory review of market competition</li>
      </ul>
    `,
    entities: ["Play", "T-Mobile Poland", "Plus", "Orange Polska", "UKE"],
    sources: [
      {
        label: "Play Official Announcement",
        url: "https://play.pl/plans/unlimited"
      },
      {
        label: "Telecom Market Analysis",
        url: "https://telecom-analysis.pl/play-pricing"
      },
      {
        label: "UKE Market Report",
        url: "https://uke.gov.pl/market-analysis-2024"
      }
    ],
    metadataJson: JSON.stringify({
      id: "2",
      title: "Play introduces new unlimited data plans",
      category: "Telecom",
      impact: { level: "Medium", score: 6.2 },
      entities: ["Play", "T-Mobile Poland", "Plus", "Orange Polska", "UKE"],
      sources: 3,
      createdAt: "2024-10-24T14:15:00Z"
    }, null, 2),
    hasDiff: false
  }
]
